import argparse
import csv
import json
import re
import sys

from aws_nuke_exporter import __version__
from aws_nuke_exporter.exceptions import InvalidExtensionError, ExportToJsonError, ExportToCsvError, ProcessingError
from aws_nuke_exporter.json_logger import JsonLogger


class AwsNukeExporter:
    ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[\d*m")
    LINE_PATTERN = re.compile(r"(\S+) - (\S+) - (\S.*?) - \[(.*?)\] - (\S.*)")

    def __init__(self, report_path, output_format="json", destination=None, logger=None):
        self.report_path = report_path
        self.output_format = output_format
        self.destination = destination or f"aws-nuke-exporter.{output_format}"
        self.logger = logger or JsonLogger(__name__)

    @staticmethod
    def _remove_ansi_codes(text):
        """Remove ANSI color codes from a string."""
        return AwsNukeExporter.ANSI_ESCAPE_PATTERN.sub("", text)

    @staticmethod
    def _parse_and_structure_details(details_array):
        """Parse and structure details from an array of strings."""
        details = {"Tag": {}}
        for detail in details_array:
            key, _, value = detail.partition(": ")
            if key.startswith("role:"):
                details.setdefault("Role", {})[key.split(":", 1)[1]] = value.strip('"')
            elif key.startswith("tag:"):
                details["Tag"][key.split(":", 1)[1]] = value.strip('"')
            else:
                details[key] = value.strip('"')
        return {k: v for k, v in details.items() if v}  # Remove empty sections

    def _parse_line_structured_details(self, line):
        """Parse a line from the AWS Nuke output."""
        clean_line = self._remove_ansi_codes(line)
        match = self.LINE_PATTERN.match(clean_line)
        if not match:
            return None

        region, resource_type, resource_id, details, status = match.groups()
        return {
            "Region": region,
            "ResourceType": resource_type,
            "ID": resource_id,
            "Details": self._parse_and_structure_details(details.split(", ")),
            "RemovalStatus": status,
        }

    def _export_data(self, data):
        """Export data to the specified format."""
        if self.output_format == "json":
            self._export_to_json(data)
        elif self.output_format == "csv":
            self._export_to_csv(data)

    def _export_to_csv(self, data):
        """Export data to CSV format."""
        try:
            self._ensure_correct_extension(".csv")
            fields = ["Region", "ResourceType", "ID", "Details", "RemovalStatus"]
            with open(self.destination, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fields)
                writer.writeheader()
                for region, resources in data.items():
                    for resource_type, resource_list in resources.items():
                        for resource in resource_list:
                            writer.writerow(resource)
            self.logger.info("Data successfully exported to CSV")
        except Exception as e:
            raise ExportToCsvError(f"failed to export data to CSV, {e}")

    def _export_to_json(self, data):
        """Export data to JSON format."""
        try:
            self._ensure_correct_extension(".json")
            with open(self.destination, "w") as file:
                json.dump(data, file, indent=4)
            self.logger.info("Data successfully exported to JSON")
        except Exception as e:
            raise ExportToJsonError(f"failed to export data to JSON, {e}")

    def _ensure_correct_extension(self, extension):
        """Ensure the destination file has the correct extension."""
        if not self.destination.endswith(extension):
            raise InvalidExtensionError(f"destination file must end with {extension}")

    def process_aws_nuke_output(self):
        """Process the AWS Nuke output file."""
        self.logger.info("Processing AWS Nuke Exporter")
        with open(self.report_path) as file:
            lines = [self._parse_line_structured_details(line) for line in file]

        data = {}
        for item in filter(None, lines):
            region_resources = data.setdefault(item["Region"], {})
            region_resources.setdefault(item["ResourceType"], []).append(item)

        self._export_data(data)
        self.logger.info("AWS Nuke Exporter processed successfully")


def main():
    try:
        parser = argparse.ArgumentParser(
            description=f"AWS Nuke Exporter - Tool for parsing and exporting AWS Nuke outputs in JSON or CSV formats. Version: {__version__}",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument("report_path", help="Path to the file containing the aws-nuke output")
        parser.add_argument("-f", "--format", choices=["json", "csv"], default="json", help="Output format")
        parser.add_argument("-d", "--destination", help="Path for the exported data file")
        parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode, no logs will be printed to stdout")
        parser.add_argument("-v", "--version", action="version", version=f"{__version__}", help="Display the version of the tool")

        args = parser.parse_args()
        logger = JsonLogger(__name__)

        if args.quiet:
            logger.mute()

        exporter = AwsNukeExporter(args.report_path, args.format, args.destination, logger)
        exporter.process_aws_nuke_output()
    except (InvalidExtensionError, ExportToJsonError, ExportToCsvError, ProcessingError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

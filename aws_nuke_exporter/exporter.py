import argparse
import csv
import json
import re

APP_VERSION = "v1.0.0"


class AwsNukeExporter:
    ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[\d*m")
    LINE_PATTERN = re.compile(r"(\S+) - (\S+) - (\S.*?) - \[(.*?)\] - (\S.*)")

    def __init__(self, report_path, output_format="json", destination=None):
        self.report_path = report_path
        self.output_format = output_format
        self.destination = destination or f"aws-nuke-exporter.{output_format}"

    @staticmethod
    def remove_ansi_codes(text):
        """Remove ANSI color codes from a string."""
        return AwsNukeExporter.ANSI_ESCAPE_PATTERN.sub("", text)

    @staticmethod
    def parse_and_structure_details(details_array):
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

    def parse_line_structured_details(self, line):
        """Parse a line from the AWS Nuke output."""
        clean_line = self.remove_ansi_codes(line)
        match = self.LINE_PATTERN.match(clean_line)
        if not match:
            return None

        region, resource_type, resource_id, details, status = match.groups()
        return {
            "Region": region,
            "ResourceType": resource_type,
            "ID": resource_id,
            "Details": self.parse_and_structure_details(details.split(", ")),
            "RemovalStatus": status,
        }

    def export_data(self, data):
        """Export data to the specified format."""
        if self.output_format == "json":
            self._export_to_json(data)
        elif self.output_format == "csv":
            self._export_to_csv(data)

    def _export_to_csv(self, data):
        """Export data to CSV format."""
        self._ensure_correct_extension(".csv")
        fields = ["Region", "ResourceType", "ID", "Details", "RemovalStatus"]
        with open(self.destination, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            for region, resources in data.items():
                for resource_type, resource_list in resources.items():
                    for resource in resource_list:
                        writer.writerow(resource)

    def _export_to_json(self, data):
        """Export data to JSON format."""
        self._ensure_correct_extension(".json")
        with open(self.destination, "w") as file:
            json.dump(data, file, indent=4)

    def _ensure_correct_extension(self, extension):
        """Ensure the destination file has the correct extension."""
        if not self.destination.endswith(extension):
            raise ValueError(f"Destination file must end with {extension}")

    def process_aws_nuke_output(self):
        """Process the AWS Nuke output file."""
        with open(self.report_path) as file:
            lines = [self.parse_line_structured_details(line) for line in file]

        data = {}
        for item in filter(None, lines):
            region_resources = data.setdefault(item["Region"], {})
            region_resources.setdefault(item["ResourceType"], []).append(item)

        self.export_data(data)


def main():
    parser = argparse.ArgumentParser(
        description=f"AWS Nuke Exporter - Tool for parsing and exporting AWS Nuke outputs in JSON or CSV formats. Version: {APP_VERSION}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("report_path", help="Path to the file containing the aws-nuke output")
    parser.add_argument("-f", "--format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("-d", "--destination", help="Path for the exported data file")
    parser.add_argument("-v", "--version", action="version", version=f"{APP_VERSION}", help="Display the version of the tool")

    args = parser.parse_args()
    exporter = AwsNukeExporter(args.report_path, args.format, args.destination)
    exporter.process_aws_nuke_output()


if __name__ == "__main__":
    main()

import csv
import json
import os
import unittest
from unittest.mock import patch

from aws_nuke_exporter.exceptions import InvalidExtensionError, ExportToJsonError, ExportToCsvError, ProcessingError
from aws_nuke_exporter.exporter import AwsNukeExporter


class TestAwsNukeExporter(unittest.TestCase):

    def setUp(self):
        """Use a fake file path for the tests and mute the logger."""
        with patch('aws_nuke_exporter.exporter.JsonLogger') as MockLogger:
            MockLogger.return_value.mute.return_value = None
            self.exporter = AwsNukeExporter("dummy_path.log", "json", "dummy_output.json")

    def test_remove_ansi_codes(self):
        """Test that ANSI codes are removed from a string."""
        test_str = "\x1b[31mThis is a test string.\x1b[0m"
        clean_str = self.exporter._remove_ansi_codes(test_str)
        self.assertEqual(clean_str, "This is a test string.")

    def test_parse_line_structured_details(self):
        """Test that a line is correctly parsed from the AWS Nuke output."""
        test_line = "eu-west-1 - EC2Instance - i-xxxxxxx - [Key: Value, tag:Name: Sample] - status"
        expected_output = {
            "Region": "eu-west-1",
            "ResourceType": "EC2Instance",
            "ID": "i-xxxxxxx",
            "Details": {"Key": "Value", "Tag": {"Name": "Sample"}},
            "RemovalStatus": "status"
        }
        self.assertEqual(self.exporter._parse_line_structured_details(test_line), expected_output)

    def test_export_to_json(self):
        """Create a fake JSON file and check that it contains the expected data and is deleted afterward."""
        test_data = {"eu-west-1": {"EC2Instance": [{"ID": "i-xxxxxxx"}]}}
        self.exporter.output_format = "json"
        self.exporter.destination = "test_output.json"
        self.exporter._export_to_json(test_data)
        self.assertTrue(os.path.isfile("test_output.json"))
        with open("test_output.json", "r") as f:
            data = json.load(f)
            self.assertEqual(data, test_data)
        os.remove("test_output.json")

        self.exporter.destination = "test_output.txt"  # Intentionally incorrect extension
        with self.assertRaises(ExportToJsonError):
            self.exporter._export_to_json(test_data)

    def test_export_to_csv(self):
        """Create a fake CSV file and check that it contains the expected data and is deleted afterward."""
        test_data = {"eu-west-1": {"EC2Instance": [{"ID": "i-xxxxxxx"}]}}
        self.exporter.output_format = "csv"
        self.exporter.destination = "test_output.csv"
        self.exporter._export_to_csv(test_data)
        self.assertTrue(os.path.isfile("test_output.csv"))
        with open("test_output.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.assertEqual(row["ID"], "i-xxxxxxx")
        os.remove("test_output.csv")

        self.exporter.destination = "test_output.txt"  # Intentionally incorrect extension
        with self.assertRaises(ExportToCsvError):
            self.exporter._export_to_csv(test_data)

    def test_ensure_correct_extension(self):
        """Test that the exporter raises an error when the extension is incorrect."""
        self.exporter.destination = "incorrect_extension.txt"
        with self.assertRaises(InvalidExtensionError):
            self.exporter._ensure_correct_extension(".json")


if __name__ == '__main__':
    unittest.main()

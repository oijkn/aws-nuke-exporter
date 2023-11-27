import unittest
from unittest.mock import patch
from aws_nuke_exporter.json_logger import JsonLogger
import logging
import json


class TestJsonLogger(unittest.TestCase):

    def test_initialization(self):
        """Test if JsonLogger is initialized with correct level and name."""
        logger = JsonLogger("test_logger", logging.DEBUG)
        self.assertEqual(logger.logger.level, logging.DEBUG)
        self.assertEqual(logger.logger.name, "test_logger")

    @patch('sys.stdout')
    def test_logging_output(self, mock_stdout):
        """Test if logging output is in JSON format."""
        logger = JsonLogger("test_logger")
        test_message = "This is a test log"
        logger.info(test_message)
        expected_output = json.dumps({"level": "INFO", "message": test_message}) + "\n"
        mock_stdout.write.assert_called_with(expected_output)

    @patch('sys.stdout')
    def test_mute_logger(self, mock_stdout):
        """Test if logger is muted correctly."""
        logger = JsonLogger("test_logger")
        logger.mute()
        logger.info("This should not be logged")
        mock_stdout.write.assert_not_called()


if __name__ == '__main__':
    unittest.main()

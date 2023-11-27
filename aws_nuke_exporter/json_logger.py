import logging
import sys


class JsonLogger:
    def __init__(self, name=__name__, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.configure_logger(level)

    def configure_logger(self, level):
        handler = logging.StreamHandler(sys.stdout)
        formatter = self.json_formatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    @staticmethod
    def json_formatter():
        return logging.Formatter('{"level": "%(levelname)s", "message": "%(message)s"}')

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def mute(self):
        """Disable logging."""
        self.logger.setLevel(logging.CRITICAL)

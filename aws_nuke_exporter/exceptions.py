class InvalidExtensionError(Exception):
    """Exception raised when the destination file has an invalid extension."""
    pass


class ExportToJsonError(Exception):
    """Exception raised during JSON export process."""
    pass


class ExportToCsvError(Exception):
    """Exception raised during CSV export process."""
    pass


class ProcessingError(Exception):
    """Exception raised during processing of AWS Nuke output."""
    pass

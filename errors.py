class AppError(Exception):
    """Base class for all application-specific errors."""
    pass

class DataNotFoundError(AppError):
    """Raised when the requested data or file is not found."""
    pass

class ProcessingError(AppError):
    """Raised when there is an issue processing the data (e.g., validation failure)."""
    pass

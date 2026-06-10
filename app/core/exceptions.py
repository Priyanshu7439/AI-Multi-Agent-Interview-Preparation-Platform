class PlatformException(Exception):
    """Base exception for the Interview Preparation Platform."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class PDFParsingException(PlatformException):
    """Exception raised when PDF parsing fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class LLMException(PlatformException):
    """Exception raised when LLM calls fail."""
    def __init__(self, message: str):
        super().__init__(message, status_code=502)

class SessionNotFoundException(PlatformException):
    """Exception raised when an interview session is not found."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class VectorStoreException(PlatformException):
    """Exception raised when vector database operations fail."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class InvalidStateException(PlatformException):
    """Exception raised when performing an action not allowed in the current state."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

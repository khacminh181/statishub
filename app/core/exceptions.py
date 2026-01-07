"""
Custom exception classes for the application.
"""


class StatishubException(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class APIKeyInvalidError(StatishubException):
    """Raised when API key is invalid or inactive."""
    def __init__(self, message: str = "Invalid API Key"):
        super().__init__(message, status_code=401)


class CreditExhaustedError(StatishubException):
    """Raised when API key has no remaining credits."""
    def __init__(self, message: str = "Out of credits"):
        super().__init__(message, status_code=402)


class OrganizationNotFoundError(StatishubException):
    """Raised when organization/company is not found."""
    def __init__(self, message: str = "Organization not found", taxcode: str = None):
        if taxcode:
            message = f"Organization with taxcode {taxcode} not found"
        super().__init__(message, status_code=404)


class DatabaseError(StatishubException):
    """Raised when database operation fails."""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class CacheError(StatishubException):
    """Raised when cache operation fails."""
    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(message, status_code=500)


class RateLimitExceededError(StatishubException):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)

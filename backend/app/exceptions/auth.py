class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an email that already exists."""
    pass

class InvalidCredentialsError(Exception):
    """Raised when authentication fails due to incorrect email or password."""
    pass

class UnverifiedEmailError(Exception):
    """Raised when the user attempts to log in without verifying their email."""
    pass

class InvalidOTPError(Exception):
    """Raised when the provided OTP is invalid."""
    pass

class OTPExpiredError(Exception):
    """Raised when the provided OTP has expired."""
    pass

class RateLimitExceededError(Exception):
    """Raised when the user has exceeded the allowed rate limit."""
    pass

class InvalidTokenError(Exception):
    """Raised when the provided JWT is malformed, has invalid signature, or is missing required claims."""
    pass

class TokenExpiredError(Exception):
    """Raised when the provided JWT has expired."""
    pass

class InsufficientPermissionsError(Exception):
    """Raised when the user does not have the required permissions for an action."""
    pass

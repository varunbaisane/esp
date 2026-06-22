class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an email that already exists."""
    pass

class InvalidCredentialsError(Exception):
    """Raised when authentication fails due to incorrect email or password."""
    pass

class InvalidTokenError(Exception):
    """Raised when the provided JWT is malformed, has invalid signature, or is missing required claims."""
    pass

class TokenExpiredError(Exception):
    """Raised when the provided JWT has expired."""
    pass

class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an email that already exists."""
    pass

class InvalidCredentialsError(Exception):
    """Raised when authentication fails due to incorrect email or password."""
    pass

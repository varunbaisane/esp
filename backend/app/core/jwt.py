from datetime import datetime, timedelta, timezone
from jose import jwt  # pyright: ignore[reportMissingImports]

from app.core.auth_config import auth_settings

def create_access_token(subject: str) -> str:
    """Create a short-lived JSON Web Token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, 
        auth_settings.JWT_SECRET_KEY, 
        algorithm=auth_settings.JWT_ALGORITHM
    )
    return encoded_jwt

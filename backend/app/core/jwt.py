from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError  # pyright: ignore[reportMissingImports]

from app.core.auth_config import auth_settings
from app.schemas.auth import TokenPayload
from app.exceptions.auth import InvalidTokenError, TokenExpiredError

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a JSON Web Token with customizable expiration."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"sub": subject, "exp": expire}
    
    encoded_jwt = jwt.encode(
        to_encode, 
        auth_settings.SECRET_KEY, 
        algorithm=auth_settings.ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JSON Web Token."""
    try:
        payload = jwt.decode(
            token,
            auth_settings.SECRET_KEY,
            algorithms=[auth_settings.ALGORITHM]
        )
        
        sub = payload.get("sub")
        if not sub:
            raise InvalidTokenError()
            
        return TokenPayload(sub=sub)
        
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()

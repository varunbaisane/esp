from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Dict, Any
from app.core.config import settings

class GoogleAuthService:
    """
    Pure infrastructure service for verifying Google ID tokens.
    It does not import any repositories, JWT logic, Redis, or business services.
    """
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verifies the Google ID token and returns the extracted payload.
        
        Args:
            token: The Google ID token (JWT) received from the client.
            
        Returns:
            A dictionary containing the token payload.
            
        Raises:
            ValueError: If the token is invalid, expired, or has the wrong audience.
        """
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID is not configured on the server.")
            
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )

            if not idinfo.get("email_verified", False):
                raise ValueError("Google account email is not verified.")

            return {
                "sub": idinfo.get("sub"),
                "email": idinfo.get("email"),
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture"),
                "email_verified": idinfo.get("email_verified"),
            }
        except ValueError as e:
            raise ValueError(f"Invalid Google token: {str(e)}")

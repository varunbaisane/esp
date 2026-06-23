from pydantic import BaseModel  # pyright: ignore[reportMissingImports]

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str

class CurrentUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    roles: list[str]

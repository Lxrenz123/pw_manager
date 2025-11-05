from pydantic import BaseModel
from app.schemas import user_schema


class AuthResponse(BaseModel):
    user: user_schema.UserLogin


class Credentials(BaseModel):
    email: str
    password: str
    recaptcha_token: str
    recaptcha_token_v2: str = None

class PreAuth(BaseModel):
    mfa_required: bool = True
    preauth_token: str
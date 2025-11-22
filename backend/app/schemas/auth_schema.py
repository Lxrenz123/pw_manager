from pydantic import BaseModel, StringConstraints, Field
from app.schemas import user_schema
from typing import Annotated, Optional


class AuthResponse(BaseModel):
    user: user_schema.UserLogin


class Credentials(BaseModel):
    email: Annotated[str, StringConstraints(max_length=320)]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    recaptcha_token: Annotated[str, StringConstraints(min_length=1, max_length=15000)]
    recaptcha_token_v2: Optional[Annotated[str, StringConstraints(max_length=15000)]] = None

class PreAuth(BaseModel):
    mfa_required: bool = True
    preauth_token: str
from pydantic import BaseModel
from schemas import user_schema


class AuthResponse(BaseModel):
    access_token: str
    user: user_schema.UserLogin
    token_type: str = "Bearer"

class Credentials(BaseModel):
    email: str
    password: str
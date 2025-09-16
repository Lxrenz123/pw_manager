from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Optional

class CreateUser(BaseModel):
    email: str
    password: str
    user_key: str  # base64 encoded
    salt: str      # base64 encoded
    iv: str        # base64 encoded

    class Config:
        orm_mode = True  

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True  

class UserOutInfoMe(BaseModel):
    id: int
    email: str
    created_at: datetime
    last_login: datetime
    mfa_enabled: bool

    @validator('mfa_enabled', pre=True)
    def convert_none_to_false(cls, v):
        return False if v is None else v

    class Config:
        orm_mode = True  



class UserLogin(BaseModel):
    id: int
    email: str
    user_key: str
    user_key: str  # base64 encoded
    iv: str        # base64 encoded
    salt: str      # base64 encoded

    class Config:
        orm_mode = True  



class User(BaseModel):
    id: int
    email: str

class UpdateUserEmail(BaseModel):
    email: str

class UpdateUserPassword(BaseModel):
    current_password: str
    password: str
from pydantic import BaseModel, validator, StringConstraints
from datetime import datetime
from typing import Annotated
from uuid import UUID

class CreateUser(BaseModel):
    email: Annotated[str, StringConstraints(max_length=320)]
    password: Annotated[str, StringConstraints(min_length=10, max_length=128)]
    user_key: Annotated[str, StringConstraints(max_length=64)]  # base64 encoded
    salt: Annotated[str, StringConstraints(max_length=24)]      # base64 encoded
    iv: Annotated[str, StringConstraints( max_length=16)]       # base64 encoded

    class Config:
        orm_mode = True  

class UserOut(BaseModel):
    id: UUID
    email: str

    class Config:
        orm_mode = True  

class UserOutInfoMe(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    last_login: datetime
    mfa_enabled: bool

    @validator('mfa_enabled', pre=True)
    @classmethod
    def convert_none_to_false(cls, v):
        return False if v is None else v

    class Config:
        orm_mode = True  



class UserLogin(BaseModel):
    id: UUID
    email: str
    user_key: str  # base64 encoded
    iv: str        # base64 encoded
    salt: str      # base64 encoded

    class Config:
        orm_mode = True  



class User(BaseModel):
    id: UUID
    email: str

class UpdateUserEmail(BaseModel):
    password: Annotated[str, StringConstraints(min_length=10, max_length=128)]
    email: Annotated[str, StringConstraints(max_length=320)]

class UpdateUserPassword(BaseModel):
    current_password: Annotated[str, StringConstraints(min_length=10, max_length=128)]
    password: Annotated[str, StringConstraints(min_length=10, max_length=128)]
    user_key: str
    iv: str

class UserDelete(BaseModel):
    password: Annotated[str, StringConstraints(min_length=10, max_length=128)]
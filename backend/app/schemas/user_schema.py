from pydantic import BaseModel

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
    password: str
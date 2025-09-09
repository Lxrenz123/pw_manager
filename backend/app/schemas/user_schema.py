from pydantic import BaseModel

class CreateUser(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True  

class UserOut(BaseModel):
    id: int
    email: str
    class Config:
        orm_mode = True  

class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    email: str

class UpdateUserEmail(BaseModel):
    email: str

class UpdateUserPassword(BaseModel):
    password: str
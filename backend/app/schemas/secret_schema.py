from pydantic import BaseModel

class CreateSecret(BaseModel):
    title: str
    data_encrypted: bytes

class UpdateSecret(BaseModel):
    title: str
    data_encrypted: bytes
    
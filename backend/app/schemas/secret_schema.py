from pydantic import BaseModel

class CreateSecret(BaseModel):
    title: str
    data_encrypted: bytes


from pydantic import BaseModel

class CreateSecret(BaseModel):
    title: str
    data_encrypted: bytes
    encrypted_secret_key: str
    secret_key_iv: str
    secret_iv: str

class UpdateSecret(BaseModel):
    title: str
    data_encrypted: bytes
    
from pydantic import BaseModel

class CreateSecret(BaseModel):
    data_encrypted: bytes
    encrypted_secret_key: str
    secret_key_iv: str
    secret_iv: str

class UpdateSecret(BaseModel):
    data_encrypted: bytes
    secret_iv: str
    encrypted_secret_key: str    
    secret_key_iv: str
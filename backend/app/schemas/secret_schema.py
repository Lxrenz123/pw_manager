from pydantic import BaseModel


class CreateSecretCredential(BaseModel):
    title: str
    username_enc: bytes = None
    password_enc: bytes = None
    url_enc: bytes = None
    note_enc: bytes = None

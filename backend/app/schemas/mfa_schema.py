from pydantic import BaseModel


class Confirm(BaseModel):
    code: str

class Verify(BaseModel):
    preauth_token: str
    code: str

class Setup(BaseModel):
    otp_uri: str
    qr_data_url: str
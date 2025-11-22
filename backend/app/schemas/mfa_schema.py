from pydantic import BaseModel, StringConstraints
from typing import Annotated


class Confirm(BaseModel):
    code: Annotated[str, StringConstraints(max_length=6)]

class Verify(BaseModel):
    preauth_token: str
    code: Annotated[str, StringConstraints(max_length=6)]

class Setup(BaseModel):
    otp_uri: str
    qr_data_url: str
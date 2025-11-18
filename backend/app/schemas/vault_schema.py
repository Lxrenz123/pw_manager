from pydantic import BaseModel
from datetime import datetime

class CreateVault(BaseModel):
    name: str


class UpdateVault(BaseModel):
    name: str

class GetVault(BaseModel):
    name: str
    created_at: datetime
    updated_at: datetime


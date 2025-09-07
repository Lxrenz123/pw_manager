from pydantic import BaseModel
from datetime import datetime, timezone

class CreateVault(BaseModel):
    vaultname: str

class GetVault(BaseModel):
    name: str
    created_at: datetime
    updated_at: datetime


from pydantic import BaseModel
from datetime import datetime, timezone

class CreateVault(BaseModel):
    owner_id: int
    name: str
    created_at: datetime
    updated_at: datetime

class GetVault(BaseModel):
    name: str
    created_at: datetime
    updated_at: datetime
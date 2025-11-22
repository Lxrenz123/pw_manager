from pydantic import BaseModel, StringConstraints
from datetime import datetime
from typing import Annotated

class CreateVault(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=64)]


class UpdateVault(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=64)]

class GetVault(BaseModel):
    name: str
    created_at: datetime
    updated_at: datetime


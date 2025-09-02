from pydantic import BaseModel
from typing import Optional
from enum import Enum

class User(BaseModel):
    email: str
    password: str
    
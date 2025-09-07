from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from typing import List
from database import Base
from .vault_model import Vault

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), nullable=False)

    vault: Mapped[List["Vault"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
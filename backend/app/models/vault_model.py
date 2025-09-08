from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from database import Base
from .secret_model import Secret
from typing import List

class Vault(Base):
    __tablename__ = "vault"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), nullable=False)
    
    owner: Mapped["User"] = relationship(back_populates="vault")
    secret: Mapped[List[Secret]] = relationship(back_populates="vault", cascade="all, delete-orphan")
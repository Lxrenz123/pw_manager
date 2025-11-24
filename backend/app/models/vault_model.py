from sqlalchemy import Integer, String, ForeignKey, DateTime, func, LargeBinary
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from app.database import Base
from .secret_model import Secret
from typing import List
import uuid
from sqlalchemy.dialects.postgresql import UUID 

class Vault(Base):
    __tablename__ = "vault"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC), server_default=func.now(), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="vault")
    secret: Mapped[List[Secret]] = relationship(back_populates="vault", cascade="all, delete-orphan")
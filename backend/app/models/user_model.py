from sqlalchemy import Integer, String, ForeignKey, DateTime, func, LargeBinary, Boolean
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from typing import List
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID 

class User(Base):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column( # changed id to a UUID to increase security.
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), server_default=func.now(), nullable=False)

    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    otp_secret: Mapped[str] = mapped_column(String, nullable=True, default=None) 

    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), server_default=func.now(), nullable=True)

    user_key: Mapped[str] = mapped_column(String, nullable=False) 
    salt: Mapped[str] = mapped_column(String, nullable=False) 
    iv: Mapped[str] = mapped_column(String, nullable=False) 
    vault: Mapped[List["Vault"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
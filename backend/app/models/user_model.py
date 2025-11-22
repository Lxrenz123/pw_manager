from sqlalchemy import Integer, String, ForeignKey, DateTime, func, LargeBinary, Boolean
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from typing import List
from app.database import Base

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
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
from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Enum, LargeBinary
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from app.database import Base
import enum

class SecretType(enum.Enum):
    CREDENTIAL = "credential"
    NOTE = "note"
    CREDITCARD = "creditcard"

class Secret(Base):
    __tablename__ = "secret"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    type: Mapped[SecretType] = mapped_column(
        Enum(SecretType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False
    )

    data_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    encrypted_secret_key: Mapped[str] = mapped_column(String, nullable=False) 
    secret_key_iv: Mapped[str] = mapped_column(String, nullable=False)

    secret_iv: Mapped[str] = mapped_column(String, nullable=False) 
    vault_id: Mapped[int] = mapped_column(Integer, ForeignKey("vault.id"), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC), server_default=func.now(), nullable=False)


    vault: Mapped["Vault"] = relationship(back_populates="secret")



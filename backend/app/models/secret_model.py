from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Enum, LargeBinary
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from database import Base
import enum

class SecretType(enum.Enum):
    CREDENTIAL = "credential"
    NOTE = "note"
    DOCUMENT = "document"

class Secret(Base):
    __tablename__ = "secret"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[SecretType] = mapped_column(Enum(SecretType), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    vault_id: Mapped[int] = mapped_column(Integer, ForeignKey("vault.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), nullable=False)


    vault: Mapped["Vault"] = relationship(back_populates="secret")

    credential: Mapped["Credential"] = relationship(back_populates="secret", uselist=False)
    note: Mapped["Note"] = relationship(back_populates="secret", uselist=False)
    document: Mapped["Document"] = relationship(back_populates="secret", uselist=False)

class Credential(Base):
    __tablename__ = "credential"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    secret_id: Mapped[int] = mapped_column(Integer, ForeignKey("secret.id"), nullable=False, unique=True) # Foreign Key 1zu1 Beziehung
    username_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    password_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    url_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    note_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)

    secret: Mapped[Secret] = relationship(back_populates="credential")

class Note(Base):
    __tablename__ = "note"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    secret_id: Mapped[int] = mapped_column(Integer, ForeignKey("secret.id"), nullable=False)
    note_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    secret: Mapped[Secret] = relationship(back_populates="note")

class Document(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    secret_id: Mapped[int] = mapped_column(Integer, ForeignKey("secret.id"), nullable=False)
    filename_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    document_blob_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    secret: Mapped[Secret] = relationship(back_populates="document")

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from models import user_model, vault_model, secret_model
from database import PgAsyncSession
from schemas import secret_schema
from auth import get_current_user

router = APIRouter(
    prefix="/secret",
    tags=["secret"],
)


@router.post("/{vault_id}/{secret_type}")
async def create_secret(session: PgAsyncSession, vault_id: int, secret_type: str, secret_data: secret_schema.CreateSecret, user: user_model.User = Depends(get_current_user)):

    stmt = select(vault_model.Vault).where(vault_model.Vault.owner_id == user.id, vault_model.Vault.id == vault_id)
    result = await session.execute(stmt)
    vault = result.scalars().first()

    if not vault:
        raise HTTPException(status_code=403, detail="Access denied!")

    try:
        secret_type_enum = secret_model.SecretType(secret_type)
    except ValueError:
        valid_types = [e.value for e in secret_model.SecretType]
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid secret type '{secret_type}'. Valid types are: {valid_types}"
        )
    
    stmt = select(secret_model.Secret).where(secret_model.Secret.title == secret_data.title, vault.id == vault_id)
    result = await session.execute(stmt)
    existing_secret = result.scalars().first()

    if existing_secret:
        raise HTTPException(status_code=400, detail=f"A secret with the title '{existing_secret.title}' exists already")
    
    secret = secret_model.Secret(
        type = secret_type_enum,
        title = secret_data.title,
        data_encrypted = secret_data.data_encrypted,
        vault_id = vault_id
    )
    session.add(secret)
    await session.commit()
    await session.refresh(secret)

    return secret


@router.get("/{vault_id}")
async def get_secret(session: PgAsyncSession, vault_id: int, user: user_model.User = Depends(get_current_user)):

    stmt = select(vault_model.Vault).where(vault_model.Vault.owner_id == user.id, vault_model.Vault.id == vault_id)
    result = await session.execute(stmt)
    vault = result.scalars().first()

    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found or access denied!")

    stmt = select(secret_model.Secret).where(secret_model.Secret.vault_id == vault_id)
    result = await session.execute(stmt)
    secrets = result.scalars().all()



    return secrets
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


@router.get("/{vault_id}")
async def get_secrets(session:PgAsyncSession, vault_id: int, user: user_model.User = Depends(get_current_user)):
    stmt = (
        select(secret_model.Secret)
        .join(vault_model.Vault)
        .where(
            secret_model.Secret.vault_id == vault_id,
            vault_model.Vault.owner_id == user.id
        )
    )

    result = await session.execute(stmt)

    secrets = result.scalars().first()

    if not secrets:
        raise HTTPException(status_code=403, detail="You don't have access to this vault")
    
    stmt = select(secret_model.Credential).where(secrets.id == secret_model.Credential.secret_id)
    result = await session.execute(stmt)
    secret_credential = result.scalars().first()


    return secret_credential, secrets

 
@router.post("/{vault_id}/credential")
async def create_secret_credential(session: PgAsyncSession, secret_credentials: secret_schema.CreateSecretCredential, vault_id: int, user: user_model.User = Depends(get_current_user)):

    vault_stmt = select(vault_model.Vault).where(
        vault_model.Vault.id == vault_id,
        vault_model.Vault.owner_id == user.id
    )
    vault_result = await session.execute(vault_stmt)
    vault = vault_result.scalars().first()
    
    if not vault:
        raise HTTPException(status_code=403, detail="You don't have access to this vault")
    
    
    
    
    stmt = select(secret_model.Secret).where(secret_model.Secret.title == secret_credentials.title)
    result = await session.execute(stmt)
    existing_secret_title = result.scalars().first()
    if existing_secret_title:
        raise HTTPException(status_code=400, detail="A secret with that title already exsists, please choose a different title")
    
    secret = secret_model.Secret(
        type = secret_model.SecretType.CREDENTIAL,
        title = secret_credentials.title,
        vault_id = vault_id   
    )
    session.add(secret)
    await session.commit()
    await session.refresh(secret)

    secret_credential = secret_model.Credential(
        secret_id = secret.id,
        username_enc = secret_credentials.username_enc,
        password_enc = secret_credentials.password_enc,
        url_enc = secret_credentials.url_enc,
        note_enc = secret_credentials.note_enc
    )
    session.add(secret_credential)
    await session.commit()
    await session.refresh(secret_credential)

    return secret_credential
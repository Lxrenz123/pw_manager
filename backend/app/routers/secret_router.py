from fastapi import APIRouter, HTTPException, status, Depends, Header, Cookie, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.models import user_model, vault_model, secret_model
from app.database import PgAsyncSession
from app.schemas import secret_schema
from app.auth import get_current_user
from app.csrf_protection import validate_csrf_token, csrf_error
from app.limiter import limiter

router = APIRouter(
    prefix="/secret",
    tags=["secret"],
)


@router.post("/{vault_id}/{secret_type}")
@limiter.limit("30/minute")
async def create_secret(request: Request, session: PgAsyncSession, vault_id: int, secret_type: str, secret_data: secret_schema.CreateSecret, user: user_model.User = Depends(get_current_user), x_csrf_token: str = Header(None), csrf_token: str = Cookie(None)):

    if not validate_csrf_token(x_csrf_token, csrf_token):
        raise HTTPException(status_code=403, detail=csrf_error)

    stmt = select(vault_model.Vault).where(vault_model.Vault.owner_id == user.id, vault_model.Vault.id == vault_id)
    result = await session.execute(stmt)
    vault = result.scalars().first()

    if not vault:
        raise HTTPException(status_code=403, detail="Access denied!")

    secret_type = secret_type.lower()

    try:
        secret_type_enum = secret_model.SecretType(secret_type)
    except ValueError:
        valid_types = [e.value for e in secret_model.SecretType]
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid secret type '{secret_type}'. Valid types are: {valid_types}"
        )
    


    secret = secret_model.Secret(
        type = secret_type_enum,
        data_encrypted = secret_data.data_encrypted,
        vault_id = vault_id,
        encrypted_secret_key = secret_data.encrypted_secret_key,
        secret_iv = secret_data.secret_iv,
        secret_key_iv = secret_data.secret_key_iv
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


@router.get("/")
async def get_all_secrets(session: PgAsyncSession, user: user_model.User = Depends(get_current_user)):

    stmt = select(secret_model.Secret).join(vault_model.Vault).where(vault_model.Vault.owner_id == user.id)
    result = await session.execute(stmt)
    user_secrets = result.scalars().all()

    if not user_secrets:
        raise HTTPException(status_code=404, detail="No secrets found")
    
    return user_secrets
    




@router.patch("/{secret_id}")
@limiter.limit("30/minute")
async def update_secret(request: Request, session: PgAsyncSession, secret_id: int, secret_data: secret_schema.UpdateSecret, user: user_model.User = Depends(get_current_user), x_csrf_token: str = Header(None), csrf_token: str = Cookie(None)):

    if not validate_csrf_token(x_csrf_token, csrf_token):
        raise HTTPException(status_code=403, detail="CSRF Protection")
    stmt = select(secret_model.Secret).join(vault_model.Vault).where(secret_model.Secret.id == secret_id, vault_model.Vault.owner_id == user.id)
    result = await session.execute(stmt)
    secret = result.scalars().first()


    if not secret:
        raise HTTPException(status_code=404, detail="Not found")


    if secret_data.data_encrypted not in (None, ""):
        secret.data_encrypted = secret_data.data_encrypted
    if secret_data.secret_iv not in (None, ""):
        secret.secret_iv = secret_data.secret_iv
    if secret_data.secret_key_iv not in (None, ""):
        secret.secret_key_iv = secret_data.secret_key_iv
    if secret_data.encrypted_secret_key not in (None, ""):
        secret.encrypted_secret_key = secret_data.encrypted_secret_key



    try:
        await session.commit()
        await session.refresh(secret)
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the secret")


    return secret

@router.delete("/{secret_id}")
async def delete_secret(session: PgAsyncSession, secret_id: int, user: user_model.User = Depends(get_current_user), x_csrf_token: str = Header(None), csrf_token: str = Cookie(None)):

    if not validate_csrf_token(x_csrf_token, csrf_token):
        raise HTTPException(status_code=403, detail=csrf_error)
    stmt = select(secret_model.Secret).join(vault_model.Vault).where(secret_model.Secret.id == secret_id, vault_model.Vault.owner_id == user.id)
    result = await session.execute(stmt)
    secret_to_delete = result.scalars().first()

    if not secret_to_delete:
        raise HTTPException(status_code=404, detail="Not found")
    
    await session.delete(secret_to_delete)
    await session.commit()

    return f"Successfully deleted secret"
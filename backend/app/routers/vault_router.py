from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from models import user_model, vault_model
from database import PgAsyncSession
from schemas import vault_schema
from auth import get_current_user

router = APIRouter(
    prefix="/vault",
    tags=["Vault"],
)


@router.get("/")
async def get_vaults(session: PgAsyncSession, current_user: user_model.User = Depends(get_current_user)):
    stmt = select(vault_model.Vault).where(vault_model.Vault.owner_id == current_user.id)
    result = await session.execute(stmt)
    vaults = result.scalars().all()
    
    return vaults



    
@router.post("/")
async def create_vault(session: PgAsyncSession, vault_data: vault_schema.CreateVault, user_id: user_model.User = Depends(get_current_user)):
     
    vault = vault_model.Vault(
    owner_id = user_id,
    name = vault_data.vaultname
    )
    session.add(vault)
    await session.commit()
    await session.refresh(vault)

    return vault

    
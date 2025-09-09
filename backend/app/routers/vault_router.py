from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
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
async def create_vault(session: PgAsyncSession, vault_data: vault_schema.CreateVault, user: user_model.User = Depends(get_current_user)):
     
    stmt = select(vault_model.Vault).where(vault_model.Vault.owner_id == user.id, vault_model.Vault.name == vault_data.name)
    result = await session.execute(stmt)
    existing_vault = result.scalars().first()
    if existing_vault:
        raise HTTPException(status_code=400, detail=f"A vault with the name {vault_data.name} already exists")

    vault = vault_model.Vault(
        owner_id = user.id,
        name = vault_data.name
    )

    session.add(vault)
    await session.commit()
    await session.refresh(vault)

    return vault

@router.patch("/{vault_id}")
async def update_vault(session: PgAsyncSession, vault_id: int, vault_data: vault_schema.UpdateVault, user: user_model.User = Depends(get_current_user)):
    stmt = select(vault_model.Vault).where(vault_model.Vault.id == vault_id, vault_model.Vault.owner_id == user.id)
    result = await session.execute(stmt)
    vault = result.scalar_one_or_none()
    
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found or not yours")
    
    if vault_data.name not in (None, ""):
        vault.name = vault_data.name
     
    await session.commit()
    await session.refresh(vault)


    return vault


@router.delete("/{vault_id}")
async def delete_vault(session: PgAsyncSession, vault_id: int, user: user_model.User = Depends(get_current_user)):

    stmt = select(vault_model.Vault).where(vault_model.Vault.id == vault_id, vault_model.Vault.owner_id == user.id)
    result = await session.execute(stmt)
    vault = result.scalar_one_or_none()

    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found or not yours")

    await session.delete(vault)   
    await session.commit()
        

    return f"Successfully deleted Vault {vault.name}"


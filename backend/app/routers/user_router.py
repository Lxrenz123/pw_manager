from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from models import user_model
from auth import hash_password, get_current_user
from database import PgAsyncSession
from schemas import user_schema

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.post("/", response_model=user_schema.UserOut)
async def create_user(user_create: user_schema.CreateUser, session: PgAsyncSession):
    stmt = select(user_model.User).where(user_model.User.email == user_create.email)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"The email {user_create.email} is not available")
    
    db_user = user_model.User(
        email=user_create.email,
        password=hash_password(user_create.password),
        user_key=user_create.user_key,
        salt=user_create.salt,
        iv=user_create.iv
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.get("/me", response_model=user_schema.UserOut)
async def read_me(current_user: user_model.User = Depends(get_current_user)):
    return current_user

@router.patch("/email", response_model=user_schema.UserOut)
async def update_email(session: PgAsyncSession, update_data: user_schema.UpdateUserEmail, user: user_model.User = Depends(get_current_user)):
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_update = result.scalars().first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found or not authenticated")
    
    if update_data.email not in (None, ""):
        user_to_update.email = update_data.email

    await session.commit()
    await session.refresh(user_to_update)

    updated_user = user_schema.UserOut(
        id = user_to_update.id,
        email = user_to_update.email
    )

    return updated_user


@router.patch("/password")
async def update_password(session: PgAsyncSession, update_data: user_schema.UpdateUserPassword, user: user_schema.User = Depends(get_current_user)):
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_update = result.scalars().first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found or not authenticated")
    
    if update_data.password not in (None, ""):
        user_to_update.password = hash_password(update_data.password)
    
    await session.commit()
    await session.refresh(user_to_update)

    return f"successfully updated users {user_to_update.email} password"
    
@router.delete("/")
async def delete_user_me(session: PgAsyncSession, user: user_model.User = Depends(get_current_user)):
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_delete = result.scalars().first()

    await session.delete(user_to_delete)
    await session.commit()

    return f"Successfully deleted user {user.email}"


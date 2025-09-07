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
    email = user_create.email,
    password = hash_password(user_create.password)
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.get("/me", response_model=user_schema.UserOut)
async def read_me(current_user: user_model.User = Depends(get_current_user)):
    return current_user

    


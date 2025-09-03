from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from models import user_model
from auth import hash_password
from database import PgAsyncSession

class CreateUser(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True  

class UserOut(BaseModel):
    id: int
    email: str
    class Config:
        orm_mode = True  
router = APIRouter(
    prefix="/users",
    tags=["User"],
)

@router.post("/", response_model=UserOut)
async def create_user(user_create: CreateUser, session: PgAsyncSession):
    stmt = select(user_model.User).where(user_model.User.email == user_create.email)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"The email {user_create.email} is not available")
    else:
        db_user = user_model.User(
        email = user_create.email,
        password = hash_password(user_create.password)
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

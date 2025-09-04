from fastapi import APIRouter, Depends, HTTPException
from schemas import user_schema, auth_schema
from auth import verify_password, create_access_token
from database import PgAsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import user_model

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login", response_model=auth_schema.AuthResponse)
async def login(session: PgAsyncSession, credentials: auth_schema.Credentials):
    email = credentials.email
    password = credentials.password
    stmt = select(user_model.User).where(email == user_model.User.email)
    result = await session.execute(stmt)
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Login failed")

    if not verify_password(password, db_user.password):
        raise HTTPException(status_code=400, detail="Login failed")

    auth_response = auth_schema.AuthResponse(
    access_token=create_access_token(email),
    user=user_schema.User.model_validate(db_user.__dict__)
    )

    return auth_response

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.models import user_model
from app.auth import hash_password, get_current_user, verify_password, check_pwned_password
from app.database import PgAsyncSession
from app.schemas import user_schema

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

    if check_pwned_password(user_create.password):
        raise HTTPException(status_code=400, detail="Your password is compromised, please choose a different password")
    
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

@router.get("/me", response_model=user_schema.UserOutInfoMe)
async def read_me(current_user: user_model.User = Depends(get_current_user)):
    return current_user

@router.get("/salt", description="get salt of user's user key")
async def get_salt(session: PgAsyncSession, user: user_model.User = Depends(get_current_user)):
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=403, detail=f"This user does not exist or you are not that user!")
    
    user_salt = user.salt

    return user_salt


@router.patch("/email", response_model=user_schema.UserOut)
async def update_email(session: PgAsyncSession, update_data: user_schema.UpdateUserEmail, user: user_model.User = Depends(get_current_user)):
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_update = result.scalars().first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found or not authenticated")
    

    stmt = select(user_model.User).where(user_model.User.email == update_data.email)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"The email {update_data.email} is not available")

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
    
    if not verify_password(update_data.current_password, user_to_update.password):
        raise HTTPException(status_code=400, detail="Wrong master password")

    if check_pwned_password(update_data.password):
        raise HTTPException(status_code=400, detail="Your new password is compromised, please choose a different password")

    
    if update_data.password not in (None, ""):
        user_to_update.password = hash_password(update_data.password)

    user_to_update.iv = update_data.iv
    user_to_update.user_key = update_data.user_key
    
    await session.commit()
    await session.refresh(user_to_update)

    return "Password successfully updated!"
    
@router.delete("/")
async def delete_user_me(session: PgAsyncSession, password: user_schema.UserDelete, user: user_model.User = Depends(get_current_user)):
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_delete = result.scalars().first()

    if not verify_password(password.password, user_to_delete.password):
        raise HTTPException(status_code=400, detail="Wrong Master password!")


    await session.delete(user_to_delete)
    await session.commit()

    return f"Successfully deleted user {user.email}"


from fastapi import APIRouter, HTTPException, status, Depends, Response, Cookie, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.models import user_model
from app.auth import hash_password, get_current_user, verify_password, check_pwned_password, revoke_access_token
from app.database import PgAsyncSession
from app.schemas import user_schema
from app.limiter import limiter
from fastapi import Request
from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
import os
from app.csrf_protection import validate_csrf_token, csrf_error

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")



@router.post("/", response_model=user_schema.UserOut)
@limiter.limit("5/minute")
async def create_user(user_create: user_schema.CreateUser, session: PgAsyncSession, request: Request):

    
    stmt = select(user_model.User).where(user_model.User.email == user_create.email)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"The email {user_create.email} is not available")

    times_pwned = check_pwned_password(user_create.password)
    if times_pwned != 0:
        raise HTTPException(status_code=400, detail=f"Your password has been seen {times_pwned} times in data breaches, please choose a different password")
    

    
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
        raise HTTPException(status_code=403, detail="This user does not exist or you are not that user!")
    
    user_salt = user.salt

    return user_salt


@router.patch("/email", response_model=user_schema.UserOut)
@limiter.limit("3/minute")
async def update_email(request: Request, session: PgAsyncSession, update_data: user_schema.UpdateUserEmail, user: user_model.User = Depends(get_current_user), x_csrf_token: str = Header(None), csrf_token: str = Cookie(None)):

    if not validate_csrf_token(x_csrf_token, csrf_token):
        raise HTTPException(status_code=403, detail=csrf_error)
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_update = result.scalars().first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found or not authenticated")
    

    if not verify_password(update_data.password, user_to_update.password):
        raise HTTPException(status_code=400, detail="Wrong master password")

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
@limiter.limit("5/minute")
async def update_password(request: Request, session: PgAsyncSession, update_data: user_schema.UpdateUserPassword, user: user_schema.User = Depends(get_current_user), x_csrf_token: str = Header(None), csrf_token: str = Cookie(None)):

    if not validate_csrf_token(x_csrf_token, csrf_token):
        raise HTTPException(status_code=403, detail=csrf_error)
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_update = result.scalars().first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found or not authenticated")
    
    if not verify_password(update_data.current_password, user_to_update.password):
        raise HTTPException(status_code=400, detail="Wrong master password")

    times_pwned = check_pwned_password(update_data.password)
    if times_pwned != 0:
        raise HTTPException(status_code=400, detail=f"Your password has been seen {times_pwned} times in data breaches, please choose a different password")
    

    
    if update_data.password not in (None, ""):
        user_to_update.password = hash_password(update_data.password)

    user_to_update.iv = update_data.iv
    user_to_update.user_key = update_data.user_key
    
    await session.commit()
    await session.refresh(user_to_update)

    return "Password successfully updated!"
    
@router.delete("/delete")
async def delete_user_me(session: PgAsyncSession, password: user_schema.UserDelete, user: user_model.User = Depends(get_current_user), x_csrf_token: str = Header(None), csrf_token: str = Cookie(None)):

    if not validate_csrf_token(x_csrf_token, csrf_token):
        raise HTTPException(status_code=403, detail=csrf_error)
    
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_delete = result.scalars().first()

    if not verify_password(password.password, user_to_delete.password):
        raise HTTPException(status_code=400, detail="Wrong Master password!")


    await session.delete(user_to_delete)
    await session.commit()

    return f"Successfully deleted user {user.email}"



@router.post("/logout")
async def logout(response: Response, request: Request, session: PgAsyncSession, user: user_model.User = Depends(get_current_user), access_token: Optional[str] = Cookie(None), x_csrf_token: str = Header(None), csrf_token: str = Cookie(None)):
   
    if not validate_csrf_token(x_csrf_token, csrf_token):
        raise HTTPException(status_code=403, detail=csrf_error)
    stmt = select(user_model.User).where(user_model.User.id == user.id)
    result = await session.execute(stmt)
    user_to_logout = result.scalars().first()

    if not user_to_logout:
        raise HTTPException(status_code=404, detail="User does not exist")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token found")

        
    if not revoke_access_token(access_token):
        raise HTTPException(status_code=401, detail="Error revoking access_token")
    

   
    response = JSONResponse({"detail": "Successfully logged out"})
    response.delete_cookie(key="access_token",path="/", domain="password123.pw")
    response.delete_cookie(key="csrf_token",path="/", domain="password123.pw")
    
    
    return response

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
import os
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.models import user_model
from sqlalchemy import select
import time



load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = os.getenv("JWT_TOKEN_EXPIRE")
PREAUTH_TOKEN_EXPIRE = os.getenv("PREAUTH_TOKEN_EXPIRE")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=int(TOKEN_EXPIRE_MINUTES))
    data = {"sub": str(user_id), "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def create_preauth_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=int(PREAUTH_TOKEN_EXPIRE))
    data = {"sub": str(user_id), "2fa": "pending", "exp": expire }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):
    error = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"},)
    except JWTError:
        raise error
    
    if payload.get("2fa") == "pending":
        raise HTTPException(status_code=403, detail="2FA verification required")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise error
    user_id = int(user_id)
    result = await session.execute(select(user_model.User).where(user_model.User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise error
    return user


def verify_preauth_token(preauth_token):
    try:
        payload = jwt.decode(preauth_token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired, login again")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid preauth token")

    if payload.get("2fa") != "pending":
        raise HTTPException(status_code=401, detail="Invalid preauth token")
    
    return int(payload.get("sub"))
    

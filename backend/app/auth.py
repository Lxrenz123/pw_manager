from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
import os
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from database import get_db

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = os.getenv("JWT_TOKEN_EXPIRE")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(id: int):
    expire = datetime.utcnow() + timedelta(minutes=int(TOKEN_EXPIRE_MINUTES))
    data = {"sub": id, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):
    error = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(staus_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"},)
    except JWTError:
        raise error
    
    sub = payload.get("sub")
    if sub is None:
        raise error
    
    
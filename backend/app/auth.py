from datetime import datetime, timedelta, UTC
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Cookie, Request
from app.database import get_db
from app.models import user_model
from sqlalchemy import select
import time
import hashlib
import requests
import os
import uuid
import redis

import redis


r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = os.getenv("JWT_TOKEN_EXPIRE")
PREAUTH_TOKEN_EXPIRE = os.getenv("PREAUTH_TOKEN_EXPIRE")


def get_token_from_cookie(access_token: Optional[str] = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access token!")
    return access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int):
    expire = datetime.now(UTC) + timedelta(minutes=int(TOKEN_EXPIRE_MINUTES))

    jti = str(uuid.uuid4())
    
    data = {"sub": str(user_id), "exp": expire, "jti": jti}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def create_preauth_token(user_id: int):
    expire = datetime.now(UTC) + timedelta(minutes=int(PREAUTH_TOKEN_EXPIRE))
    jti = str(uuid.uuid4())
    data = {"sub": str(user_id), "2fa": "pending", "exp": expire, "jti": jti}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(get_token_from_cookie), session: AsyncSession = Depends(get_db)):

    error = HTTPException(status_code=401, detail="Could not validate credentials")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise error
    
    if payload.get("2fa") == "pending":
        raise HTTPException(status_code=403, detail="2FA verification required")
    
    if is_blacklisted(payload.get("jti")):
        raise error

    
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
    

def check_pwned_password(password: str):
    hashed_password = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()

    prefix = hashed_password[:5]
    suffix = hashed_password[5:]

    response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
    if response.status_code != 200:
        raise RuntimeError("Error fetching data from pwned API")

    hashes = (line.split(":") for line in response.text.splitlines())

    for hash_suffix, count in hashes:
        if hash_suffix == suffix:
            return int(count)


    return 0


def revoke_access_token(access_token: str) -> bool:

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not jti:
            raise HTTPException(status_code=400, detail="No jti in token")
        if not exp:
            raise HTTPException(status_code=400, detail="No expiration time in token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
    current_time = int(time.time())
    expire_seconds = exp - current_time
    if expire_seconds <= 0:
   
        return False

    key = f"blacklist:{jti}"
    r.set(key, "true", ex=expire_seconds)

    return True

def is_blacklisted(jti: str) -> bool:  

    key = f"blacklist:{jti}"
    
    return r.exists(key) == 1


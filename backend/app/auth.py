from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import os
from jose import jwt, JWTError
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = os.getenv("JWT_TOKEN_EXPIRE")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=int(TOKEN_EXPIRE_MINUTES))
    data = {"user": email, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

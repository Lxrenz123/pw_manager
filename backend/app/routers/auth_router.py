from fastapi import APIRouter, Depends, HTTPException
from app.schemas import user_schema, auth_schema, mfa_schema
from app.auth import verify_password, create_access_token, create_preauth_token, verify_preauth_token
from app.database import PgAsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import user_model
from datetime import datetime
from app.twofa import verifiy_totp
from typing import Union

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login", response_model=Union[auth_schema.AuthResponse, auth_schema.PreAuth])
async def login(session: PgAsyncSession, credentials: auth_schema.Credentials):
    email = credentials.email
    password = credentials.password
    stmt = select(user_model.User).where(email == user_model.User.email)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Login failed")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Login failed")
    
    if user.mfa_enabled:
        response_preauth = auth_schema.PreAuth(
            mfa_required=True,
            preauth_token=create_preauth_token(user.id)
        )

        return response_preauth

    auth_response = auth_schema.AuthResponse(
        access_token=create_access_token(user.id),
        user=user_schema.UserLogin(
            id=user.id,
            email=user.email,
            user_key=user.user_key,
            salt=user.salt,
            iv=user.iv
        )
    )

    user.last_login = datetime.utcnow()

    session.add(user)
    await session.commit()
    await session.refresh(user)
    

    return auth_response

@router.post("/2fa-verify", response_model=auth_schema.AuthResponse)
async def verify_2fa(session: PgAsyncSession, mfadata: mfa_schema.Verify):
    
    if not verify_preauth_token(mfadata.preauth_token):
        raise HTTPException(status_code=400, detail="Invalid Token")
    
    user_id = verify_preauth_token(mfadata.preauth_token)

    stmt = select(user_model.User).where(user_model.User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=401, detail="Invalid token or 2FA not enabled")
    
    if not verifiy_totp(user.otp_secret, mfadata.code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    auth_response = auth_schema.AuthResponse(
    access_token=create_access_token(user.id),
    user=user_schema.UserLogin(
        id=user.id,
        email=user.email,
        user_key=user.user_key,
        salt=user.salt,
        iv=user.iv
        )
    )

    user.last_login = datetime.utcnow()

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return auth_response


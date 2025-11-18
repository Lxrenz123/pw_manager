from fastapi import APIRouter, Depends, HTTPException, Request, Cookie, Response
from app.schemas import user_schema, auth_schema, mfa_schema
from app.auth import verify_password, create_access_token, create_preauth_token, verify_preauth_token
from app.database import PgAsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import user_model
from datetime import datetime, UTC
from app.twofa import verifiy_totp
from typing import Union
from app.recaptcha import verify_recaptchav3, verify_recaptchav2
from app.limiter import limiter
from app.csrf_protection import create_csrf_token
from app.logger import logger

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/login", response_model=Union[auth_schema.AuthResponse, auth_schema.PreAuth])
@limiter.limit("5/minute")
async def login(response: Response, session: PgAsyncSession, credentials: auth_schema.Credentials, request: Request):
    client_ip = request.client.host

    score = await verify_recaptchav3(token=credentials.recaptcha_token, action="login", remote_ip=client_ip)

    if score < 0.7:
        if not credentials.recaptcha_token_v2:
            raise HTTPException(status_code=403, detail="Please solve reCAPTCHA checkbox")
        if not await verify_recaptchav2(token=credentials.recaptcha_token_v2, remote_ip=client_ip):
            raise HTTPException(status_code=403, detail="Captcha error")

    email = credentials.email
    password = credentials.password
    stmt = select(user_model.User).where(user_model.User.email == email)
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
        user=user_schema.UserLogin(
            id=user.id,
            email=user.email,
            user_key=user.user_key,
            salt=user.salt,
            iv=user.iv
        )
    )


    user.last_login = datetime.now(UTC)

    session.add(user)
    await session.commit()
    await session.refresh(user)

  
    response.set_cookie(
        key="access_token",
        value=f"{create_access_token(user.id)}",
        httponly=True,      
        secure=True,        
        samesite="strict",     
        max_age=1800,       
        path="/",           
        domain="password123.pw" 
    )
    response.set_cookie(
        key="csrf_token",
        value=create_csrf_token(),
        httponly=False,      
        secure=True,        
        samesite="strict",     
        max_age=1800,       
        path="/",           
        domain="password123.pw" 
    )

    request.state.user = user
    return auth_response

@router.post("/2fa-verify", response_model=auth_schema.AuthResponse)
@limiter.limit("3/minute")
async def verify_2fa(response: Response, request: Request,session: PgAsyncSession, mfadata: mfa_schema.Verify):
    
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
    user=user_schema.UserLogin(
        id=user.id,
        email=user.email,
        user_key=user.user_key,
        salt=user.salt,
        iv=user.iv
        )
    )

    user.last_login = datetime.now(UTC)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    response.set_cookie(
        key="access_token",
        value=f"{create_access_token(user.id)}",
        httponly=True,      
        secure=True,        
        samesite="strict",     
        max_age=1800,       
        path="/",           
        domain="password123.pw" 
    )
    response.set_cookie(
        key="csrf_token",
        value=create_csrf_token(),
        httponly=False,      
        secure=True,        
        samesite="strict",     
        max_age=1800,       
        path="/",           
        domain="password123.pw" 
    )


    return auth_response


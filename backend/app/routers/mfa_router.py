from fastapi import APIRouter, Depends, HTTPException
from app.schemas import user_schema, auth_schema, mfa_schema
from app.auth import verify_password, create_access_token
from app.database import PgAsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import user_model
from datetime import datetime
from app.twofa import generate_otp_secret, get_provisioning_uri, qrcode_data_url, verifiy_totp 
from app.auth import get_current_user

router = APIRouter(prefix="/2fa", tags=["2fa"])

@router.post("/setup", response_model=mfa_schema.Setup)
async def setup_2fa(session: PgAsyncSession, user: user_model.User = Depends(get_current_user)):
    
    if user.mfa_enabled:
        raise HTTPException(status_code=400, detail="2FA already enabled")

    secret = generate_otp_secret()

    user.otp_secret = secret
    session.add(user)
    await session.commit()
    await session.refresh(user)

    otp_uri = get_provisioning_uri(user.email, secret, issuer="Password123")
    qr_data_url = qrcode_data_url(otp_uri)

    response = mfa_schema.Setup(
        otp_uri=otp_uri,
        qr_data_url=qr_data_url
    )
    
    return response

@router.post("/confirm")
async def confirm_2fa(session: PgAsyncSession, code: mfa_schema.Confirm, user: user_model.User = Depends(get_current_user)):
    if not user.otp_secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
    
    ok = verifiy_totp(user.otp_secret, code.code)

    if not ok:
        raise HTTPException(status_code=400, detail="Invalid Code")
    
    user.mfa_enabled = True

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return "2 Factor Authentication is now ready!"

@router.post("/disable")
async def disable_2fa(session: PgAsyncSession, code: mfa_schema.Confirm, user: user_model.User = Depends(get_current_user)):
    if not user.mfa_enabled:
        raise HTTPException(status_code=400, detail="2FA is already disabled")
    
    if not verifiy_totp(user.otp_secret, code.code):
        raise HTTPException(status_code=400, detail="Invalid Code")
    
    user.mfa_enabled = False
    user.otp_secret = None
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return "2FA was successfully disabled"


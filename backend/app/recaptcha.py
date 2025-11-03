import os

from fastapi import HTTPException
import httpx


SECRET_CAPTCHA_KEYV3 = os.getenv("RECAPTCHA_SECRET_KEY")
SECRET_CAPTCHA_KEYV2 = os.getenv("RECAPTCHAV2_SECRET_KEY")

url = "https://www.google.com/recaptcha/api/siteverify"

async def verify_recaptchav3(token: str, action: str, remote_ip: str | None = None):
    
    data = {
        "secret": SECRET_CAPTCHA_KEYV3,
        "response": token
    }
    if remote_ip:
        data["remoteip"] = remote_ip

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        result = response.json()


    if not result.get("success", False):
        raise HTTPException(status_code=400, detail="Invalid reCAPTCHA")

    if result.get("action") != action:
        raise HTTPException(status_code=400, detail="reCAPTCHA action mismatch")

    if result.get("score", 0.0) <= 0.9:
        return result.get("score")

    return True


async def verify_recaptchav2(token: str, remote_ip: str | None = None):
    data = {
        "secret": SECRET_CAPTCHA_KEYV2,
        "response": token
    }
    if remote_ip:
        data["remoteip"] = remote_ip
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        result = response.json()

    if not result.get("success"):
        raise HTTPException(status_code=400, detail="Invalid reCAPTCHA (v2)")
    
    return True
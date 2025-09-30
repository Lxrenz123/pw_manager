import os
from dotenv import load_dotenv
import requests
from fastapi import HTTPException


load_dotenv()

SECRET_CAPTCHA_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

def verify_recaptcha(token: str, action: str, remote_ip: str | None = None):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": SECRET_CAPTCHA_KEY,
        "response": token
    }
    if remote_ip:
        data["remoteip"] = remote_ip
    
    response = requests.post(url, data=data)
    result = response.json()

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail="Invalid reCAPTCHA")

    if result.get("action") != action:
        raise HTTPException(status_code=400, detail="reCAPTCHA action mismatch")

    if result.get("score", 0.0) < 0.7:
        raise HTTPException(status_code=403, detail="Suspicious activity detected")


    
    return True
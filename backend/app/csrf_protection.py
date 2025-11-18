from fastapi import HTTPException, Cookie
import os
import hashlib
import secrets
import hmac
from typing import Optional

CSRF_HMAC_SECRET = os.getenv("CSRF_HMAC_SECRET")

csrf_error = "CSRF Protection"


def create_csrf_token():

    random_value = secrets.token_hex(16)

    signature = hmac.new(CSRF_HMAC_SECRET.encode(), msg=random_value.encode(), digestmod=hashlib.sha256).hexdigest()
    
    token = f"{random_value}:{signature}"

    return token
    

def validate_csrf_token(csrf_token_header: str, csrf_token_cookie: Optional[str] = Cookie(None)):

    if not csrf_token_cookie or not csrf_token_header:
        raise HTTPException(status_code=403, detail="Missing csrf token!")
    
    if csrf_token_header != csrf_token_cookie:
        raise HTTPException(status_code=403, detail="Missing csrf token!")
    
    try:
        value, signature = csrf_token_cookie.split(":")
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid CSRF token format")

    expected_signature = hmac.new(CSRF_HMAC_SECRET.encode(), msg=value.encode(), digestmod=hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=403, detail="Invalid CSRF token signature")



    return True
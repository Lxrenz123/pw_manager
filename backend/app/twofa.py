import pyotp
import qrcode
import io
import base64


def generate_otp_secret() -> str:
    return pyotp.random_base32()

def get_provisioning_uri(username: str, secret: str, issuer: str = "Password123"):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)

def qrcode_data_url(otp_uri: str) -> str:
    img = qrcode.make(otp_uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def verifiy_totp(secret: str, code: str, window: int = 1) -> bool:
    totp = pyotp.TOTP(secret)
    
    return totp.verify(code, valid_window=window)
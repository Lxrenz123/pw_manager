from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.routers import user_router, auth_router, vault_router, secret_router, mfa_router
from fastapi.middleware.cors import CORSMiddleware
from app.limiter import limiter
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


async def generic_error_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"}
    )



app = FastAPI(title="Password Manager", root_path="/api")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, generic_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://password123.pw","*"], # * nur für debuggen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



routers = [user_router.router, auth_router.router, vault_router.router, secret_router.router, mfa_router.router]

for router in routers:
    app.include_router(router)
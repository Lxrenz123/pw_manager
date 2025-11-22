from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.routers import user_router, auth_router, vault_router, secret_router, mfa_router
from fastapi.middleware.cors import CORSMiddleware
from app.limiter import limiter
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request

from app.logger import logger, LogMiddleware, setup_error_logging



async def generic_error_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"}
    )

app = FastAPI(title="Password Manager", root_path="/api")
app.add_middleware(LogMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, generic_error_handler)


setup_error_logging(app)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://password123.pw"], 
    allow_credentials=True,
    allow_methods=["POST", "PATCH", "DELETE", "GET"],
    allow_headers=["X-CSRF-TOKEN", "Content-Type", "accept"],
)



routers = [user_router.router, auth_router.router, vault_router.router, secret_router.router, mfa_router.router]

for router in routers:
    app.include_router(router)
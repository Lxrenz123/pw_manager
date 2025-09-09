from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from routers import user_router, auth_router, vault_router, secret_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Password Manager", root_path="/api")

items = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"Hi"}


routers = [user_router.router, auth_router.router, vault_router.router, secret_router.router]

for router in routers:
    app.include_router(router)
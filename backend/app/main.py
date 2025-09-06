from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from routers import user_router, auth_router
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

class Item(BaseModel):
    text: str #if no default value then it is required
    is_done: bool = False
    haha: str = None

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/items", response_model=list[Item], description="hahah")
def create_item(item: Item):
    items.append(item)
    return items

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    
    if item_id < len(items):   
        requesteditem = items[item_id]
        return requesteditem
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


routers = [user_router.router, auth_router.router]

for router in routers:
    app.include_router(router)
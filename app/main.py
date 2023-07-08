import uvicorn
from fastapi import FastAPI

from app.order.order import router as order_router
from app.user.user import router as user_router
from app.store.store import router as store_router

app = FastAPI()

@app.get("/")
async def greeting():
  return {"message": "Hello World"}

app.include_router(user_router, prefix="/user")
app.include_router(order_router, prefix="/order")
app.include_router(store_router, prefix="/store")

if __name__ == '__main__':
  uvicorn.run("app.main", host="0.0.0.0", port=8000, reload=True)
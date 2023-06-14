from fastapi import FastAPI

from order.order import router as order_router
from user.user import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/user")
app.include_router(order_router, prefix="/order")

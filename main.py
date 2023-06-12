from fastapi import FastAPI

from user.user import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/user")
app.include_router(user_router, prefix="/cart")

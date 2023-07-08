from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class StoreLogin(BaseModel):
    storeId: str
    storePassword: str
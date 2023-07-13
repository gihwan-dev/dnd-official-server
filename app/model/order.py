from typing import List

from pydantic import BaseModel

from app.model.store import Item


class Order(BaseModel):
    userEmail: str
    storeId: str
    items: List[Item]
    totalAmount: int
    latitude: str
    longitude: str
    date: str
    payMethod: str
    status: str
    request: str

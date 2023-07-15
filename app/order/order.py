from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.lib.db.pymongo_connect_database import connect_database
from app.model.order import Order

router = APIRouter()


class Item(BaseModel):
    name: str
    description: str
    price: int
    amount: int


class AddItem:
    userEmail: str
    items: List[Item]


class GetOrder(BaseModel):
    userEmail: str


class Test(BaseModel):
    data: str


@router.post("/")
async def create_order(order_info: Order):
    client = connect_database()

    new_items = [item.dict() for item in order_info.items]

    new_order = Order(
        userEmail=order_info.userEmail,
        storeId=order_info.storeId,
        items=new_items,
        totalAmount=order_info.totalAmount,
        latitude=order_info.latitude,
        longitude=order_info.longitude,
        date=order_info.date,
        payMethod=order_info.payMethod,
        status=order_info.status,
        request=order_info.request
    )

    order_result = client.get_database("dnd").get_collection("orders").insert_one(new_order.dict())

    if (order_result.acknowledged):
        return {"accepted": True}

    return {"accepted": False}

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.lib.db.pymongo_connect_database import connect_database

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


class CompleteOrder(BaseModel):
    userEmail: str
    userName: str
    total: int
    payMethod: str
    payDate: str
    cart: List[Item]


class Test(BaseModel):
    data: str


@router.post("/")
async def get_order(user: GetOrder):
    client = connect_database()

    userOrder = client.get_database("dnd").get_collection("orders").find_one({"userEmail": user.userEmail})

    if userOrder:
        client.close()
        return {
            "userEmail": userOrder["userEmail"],
            "userName": userOrder["userName"],
            "total": userOrder["total"],
            "payMethod": userOrder["payMethod"],
            "payDate": userOrder["payDate"],
            "cart": userOrder["cart"],
            "isValidate": True
        }

    client.close()
    return {"isValidate": False}


@router.post("/complete")
async def complete_order(order_info: CompleteOrder):
    client = connect_database()

    items = [item.dict() for item in order_info.cart]

    order_result = client.get_database("dnd").get_collection("orders").insert_one({
        "userEmail": order_info.userEmail,
        "userName": order_info.userEmail,
        "total": order_info.total,
        "payMethod": order_info.payMethod,
        "payDate": order_info.payDate,
        "cart": items,
    })

    if (order_result.acknowledged):
        return {"accepted": True}

    return {"accepted": False}

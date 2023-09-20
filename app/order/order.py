from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.lib.db.pymongo_connect_database import connect_database
from app.model.order import Order

from bson import ObjectId

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

class CheckOrderInfo(BaseModel):
    userEmail: str


class StatusUpdateRequest(BaseModel):
    order_id: str
    new_status: str

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

@router.get("/count")   
async def get_order_count():
    client = connect_database()

    order_collection = client.get_database("dnd").get_collection("orders")

    order_count = order_collection.count_documents({})

    client.close()

    return {"order_count" : order_count}

@router.post("/check")
async def check_order_info(request: CheckOrderInfo):
    client = connect_database()
    orders = client.get_database("dnd").get_collection("orders").find({ "userEmail": request.userEmail })

    orders = list(orders)
    client.close()

    if not orders:
        return { "isValidate": False }

    return {"isValidate": True}



@router.get("/info")
async def get_order_info():
    client = connect_database()

    order_collection = client.get_database("dnd").get_collection("orders")

    orders = list(order_collection.find())
    orders_list = []

    for order in orders:
        order['_id'] = str(order['_id'])
        orders_list.append(order)

    client.close()

    return {"orders" : orders}


@router.post("/Status")
async def Status_change(request: StatusUpdateRequest):
    client = connect_database()

    order_collection = client.get_database("dnd").get_collection("orders")


    result = order_collection.update_one(
        {"_id": ObjectId(request.order_id)},
        {"$set" : {"status": request.new_status}}
    )

    if result.modified_count:
        client.close()
        return {"status": "success", "message": "Order status updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

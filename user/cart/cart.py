from typing import List

from fastapi import APIRouter

router = APIRouter


class Item:
    name: str
    description: str
    price: int
    amount: int


class AddItem:
    userEmail: str
    items: List[Item]


@router.post("/")
async def add_item(AddItem):
    return

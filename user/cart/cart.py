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


class GetOrder:
    userEmail: str


@router.post("/order")
async def order_item(AddItem):
    # 주문 진행 함수 작성
    # order 데이터베이스에 주문정보 저장.
    return


@router.post("/")
async def get_order(user: GetOrder):
    # 만약 주문 목록 데이터베이스에 해당 이름의 주문자가 있다면 주문 상태임을 알려줌.
    return

# 주문 정보 삭제하는 함수 필요

from typing import List, Optional

from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: int
    description: str
    available: bool
    # 주문수
    # amount: int


class Daily(BaseModel):
    date: int
    total: int
    amount: int


class Month(BaseModel):
    month: int
    total: int
    amount: int
    day_list: List[Daily]


class Year(BaseModel):
    year: int
    total: int
    amount: int
    month_list: List[Month]


class StoreModel(BaseModel):
    storeId: str  # 필수
    storePassword: str  # 필수
    storeName: str  # 필수
    storeAddress: str  # 필수
    storeDetailAddress: str  # 필수
    storePostCode: str  # 필수
    status: bool
    items: Optional[List[Item]]
    storeConTactNumber: str  # 필수
    certification: str  # 필수
    ownerName: str  # 필수
    tag: str  # 필수
    dailyCount: Optional[int]
    workingInfo: Optional[List[str]]
    statics: Optional[List[Year]]
    todoList: Optional[List[str]]
    total: int
    startTime: int
    years: List[Year]

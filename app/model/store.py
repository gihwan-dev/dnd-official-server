from typing import List, Optional

from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: int
    description: str
    available: bool


class Daily(BaseModel):
    date: str
    total: int
    amount: int


class Month(BaseModel):
    month: str
    day_list: List[Daily]


class Year(BaseModel):
    year: str
    month_list: List[Month]


class StoreModel(BaseModel):
    storeId: str  # 필수
    storePassword: str  # 필수
    storeName: str  # 필수
    storeAddress: str  # 필수
    storeDetailAddress: str  # 필수
    storePostCode: str  # 필수
    status: bool
    items: Optional[List[Year]]
    storeConTactNumber: str  # 필수
    certification: str  # 필수
    ownerName: str  # 필수
    tag: str  # 필수
    dailyCount: Optional[int]
    workingInfo: Optional[List[str]]
    statics: Optional[List[Year]]
    todoList: Optional[List[str]]
    startTime: int

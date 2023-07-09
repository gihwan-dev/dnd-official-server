from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    name: str
    price: int
    description: str
    available: bool
class StoreModel(BaseModel):
    storeId: str  # 필수
    storePassword: str  # 필수
    storeName: str  # 필수
    storeAddress: str   # 필수
    storeDetailAddress: str  # 필수
    storePostCode: str  # 필수
    status: bool
    items: List[Item]
    storeConTactNumber: str  # 필수
    certification: str  # 필수
    ownerName: str  # 필수
    tag: str  # 필수
    dailyCount: int
    workingInfo: List[str]



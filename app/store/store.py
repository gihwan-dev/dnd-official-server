import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, UploadFile, Form
from fastapi import HTTPException, status, Request
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.lib.db.pymongo_connect_database import connect_database
from app.lib.hash.hash import comparePassword, hashPassword
from app.model.store import StoreModel, Daily, Month, Year, Item

SECRET_KEY = "ex5eYU5PgIQDyyAN+aJFBm+3ADNAV8V7g168sgRZ/7w="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


def create_access_token(data: dict):
    to_encode = data.copy()

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_store_id(entered_jwt: str):
    payload = jwt.decode(token=entered_jwt, key=SECRET_KEY, algorithms=[ALGORITHM])
    storeId = payload["storeId"]
    return storeId


class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    storeId: str | None = None


class StoreLogin(BaseModel):
    storeId: str
    storePassword: str


class StoreOnlyId(BaseModel):
    storeId: str


class CreateStore(BaseModel):
    storeId: str
    storePassword: str
    storeAddress: str
    storeDetailAddress: str
    storePostCode: str
    storeName: str
    ownerName: str
    certification: str
    storeContactNumber: str
    tag: str


class CreateStoreResponse(BaseModel):
    isCreated: bool


class CheckStoreId(BaseModel):
    storeId: str


@router.post("/check")
async def check_id(store: CheckStoreId):
    client = connect_database()
    user = client.get_database("dnd").get_collection("stores").find_one({"storeId": store.storeId})

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 id 입니다."
        )

    client.close()
    return {
        "isValid": True
    }


@router.post("/login", response_model=Token)
async def auth_store(store: StoreLogin):
    client = connect_database()
    user = client.get_database("dnd").get_collection("stores").find_one({"storeId": store.storeId})

    if not user:
        client.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 id의 유저가 존재 하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    is_valid = comparePassword(store.storePassword, user["storePassword"])

    if not is_valid:
        client.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치 하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    client.close()
    access_token = create_access_token(
        data={"storeId": store.storeId}
    )
    return {"access_token": access_token}


@router.post("/")
async def create_store(store: CreateStore):
    client = connect_database()

    collection = client.get_database("dnd").get_collection("stores")
    user = collection.find_one({"storeId": store.storeId})

    if user:
        client.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 id 입니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    hashed_password = hashPassword(store.storePassword)

    now = datetime.now()

    year_now = now.year
    month_now = now.month
    day_now = now.day

    new_day = Daily(
        date=day_now,
        total=0,
        amount=0
    )

    new_month = Month(
        month=month_now,
        total=0,
        amount=0,
        day_list=[new_day]
    )

    new_year = Year(
        year=year_now,
        total=0,
        amount=0,
        month_list=[new_month]
    )

    new_store = StoreModel(
        storeId=store.storeId,
        storePassword=hashed_password,
        storeName=store.storeName,
        storeAddress=store.storeAddress,
        storeDetailAddress=store.storeDetailAddress,
        storePostCode=store.storePostCode,
        status=False,
        items=[],
        storeConTactNumber=store.storeContactNumber,
        certification=store.certification,
        ownerName=store.ownerName,
        tag=store.tag,
        dailyCount=0,
        workingInfo=[],
        statics=[],
        todoList=[],
        startTime=0,
        years=[new_year],
        total=0
    )

    insert_result = collection.insert_one(new_store.dict())

    if not insert_result.acknowledged:
        client.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가게를 생성 하는데 실패했습니다. 다시 시도해 주세요"
        )
    client.close()
    return {
        "isCreated": True
    }


@router.get("/", response_model=StoreModel)
async def get_store(request: Request):
    encoded_id = request.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()
    current_store = client.get_database("dnd").get_collection("stores").find_one({"storeId": storeId})
    client.close()
    return current_store


class AddMemoRequest(BaseModel):
    memo: str


@router.post("/memo")
async def add_memo(data: AddMemoRequest, req: Request):
    encoded_id = req.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()
    store_collection = client.get_database("dnd").get_collection("stores")
    store = store_collection.find_one({"storeId": storeId})

    existing_todo: List[str] = store["todoList"].copy()
    existing_todo.append(data.memo)

    updated_todo = existing_todo.copy()

    update_result = store_collection.update_one({"storeId": storeId}, {"$set": {"todoList": updated_todo}})

    client.close()

    if not update_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="메모 추가에 실패했습니다.")


class DeleteMemoRequest(BaseModel):
    index: int


@router.delete("/memo")
async def delete_memo(data: DeleteMemoRequest, req: Request):
    encoded_id = req.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()
    store_collection = client.get_database("dnd").get_collection("stores")
    store = store_collection.find_one({"storeId": storeId})

    existing_todo: List[str] = store["todoList"].copy()
    del existing_todo[data.index]

    updated_todo = existing_todo.copy()

    update_result = store_collection.update_one({"storeId": storeId}, {"$set": {"todoList": updated_todo}})

    client.close()

    if not update_result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="메모 삭제에 실패했습니다."
        )


class StoreStartRequest(BaseModel):
    startTime: int


@router.post("/start")
async def start_store(data: StoreStartRequest, req: Request):
    encoded_id = req.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()
    store_collection = client.get_database("dnd").get_collection("stores")

    update_result = store_collection.update_one({"storeId": storeId},
                                                {"$set": {"status": True, "startTime": data.startTime}})
    client.close()

    if not update_result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="프로그램을 시작하는데 실패했습니다."
        )


@router.post("/end")
async def end_store(req: Request):
    encoded_id = req.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()
    store_collection = client.get_database("dnd").get_collection("stores")

    update_result = store_collection.update_one({"storeId": storeId}, {"$set": {"status": False, "startTime": 0}})
    client.close()

    if not update_result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="프로그램을 종료하는데 실패했습니다."
        )


class TestInsertYear(BaseModel):
    year: int
    total: int
    amount: int
    month_list: List[Month]


@router.post("/test")
async def insertYear(data: TestInsertYear):
    client = connect_database()
    store_collection = client.get_database("dnd").get_collection("stores")

    test = store_collection.find_one({"storeId": "string"})

    new_data = test.copy()

    new_data["years"].append(data.dict())

    insert_result = store_collection.update_one({"storeId": "string"}, {"$set": {"years": new_data["years"]}})

    if (insert_result.acknowledged):
        client.close()
        return {
            "isInserted": True
        }
    client.close()
    return {
        "isInserted": False
    }


@router.post("/item")
async def create_item(req: Request, image: UploadFile = Form(...), name: str = Form(...),
                      description: str = Form(...), price: int = Form(...)):
    encoded_id = req.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()
    collections = client.get_database("dnd").get_collection("stores")

    store = collections.find_one({"storeId": storeId})

    updating_items = store["items"].copy()

    new_item = Item(
        name=name,
        price=price,
        description=description,
        available=True
    )

    updating_items.append(new_item.dict())

    insert_item = collections.update_one({"storeId": storeId}, {"$set": {"items": updating_items}})

    if not insert_item.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="메뉴를 추가하는데 실패했습니다."
        )

    content = await image.read()

    abs_cwd = os.getcwd()

    with open(os.path.join(abs_cwd + "/app/store/images", storeId + "_" + name + ".jpeg"), "wb") as fp:
        fp.write(content)

    client.close()


@router.get("/item/{filename}")
async def get_image(filename: str):
    abs_cwd = os.getcwd()
    return FileResponse(f'{abs_cwd}/app/store/images/{filename}.jpeg', media_type="image/jpeg")


@router.get("/order")
async def get_order(req: Request):
    encoded_id = req.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()

    order_collection = client.get_database("dnd").get_collection("orders")

    existing_store_orders = order_collection.find({"storeId": storeId})

    updated_orders = []

    for order in existing_store_orders:
        new_order = order.copy()
        new_order["_id"] = str(new_order["_id"])
        updated_orders.append(new_order)

    client.close()
    return updated_orders

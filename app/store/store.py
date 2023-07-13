from datetime import datetime
from typing import List

from fastapi import APIRouter
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.lib.db.pymongo_connect_database import connect_database
from app.lib.hash.hash import comparePassword, hashPassword
from app.model.store import StoreModel, Daily, Month, Year

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
        years=[new_year]
    )

    insert_result = collection.insert_one(new_store.dict())

    if not insert_result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가게를 생성 하는데 실패했습니다. 다시 시도해 주세요"
        )

    return {
        "isCreated": True
    }


@router.get("/", response_model=StoreModel)
async def get_store(request: Request):
    encoded_id = request.cookies.get("jwt")
    storeId = get_current_store_id(encoded_id)

    client = connect_database()
    current_store = client.get_database("dnd").get_collection("stores").find_one({"storeId": storeId})

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

    if not update_result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="프로그램을 종료하는데 실패했습니다."
        )

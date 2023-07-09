from fastapi import APIRouter
from pydantic import BaseModel
from app.lib.db.pymongo_connect_database import  connect_database
from app.lib.hash.hash import comparePassword, hashPassword
from app.model.store import StoreModel
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "ex5eYU5PgIQDyyAN+aJFBm+3ADNAV8V7g168sgRZ/7w="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_storeId(entered_jwt: str):
    payload = jwt.decode(token=entered_jwt, key=SECRET_KEY, algorithms=[ALGORITHM])

    storeId = payload.get("sub")

    return storeId


class Token(BaseModel):
    access_token: str
    token_type: str


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

class CreateStoreResponse(BaseModel):
    isCreated: bool
@router.post("/login", response_model=Token)
async def auth_store(store: StoreLogin):
    client = connect_database()
    user = client.get_database("dnd").get_collection("stores").find_one({"storeId": store.storeId})

    if not user:
        client.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 id의 유저가 존재 하지 않습니다.",
            headers={"WWW-Authenticate" : "Bearer"}
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["storeId"], }, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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

    new_store = StoreModel()
    new_store.storeId = store.storeId
    new_store.storePassword = hashed_password
    new_store.storeName = store.storeName,
    new_store.storeAddress = store.storeAddress
    new_store.storeDetailAddress = store.storeDetailAddress,
    new_store.storePostCode = store.storePostCode
    new_store.status = False,
    new_store.items = [],
    new_store.storeConTactNumber = "",
    new_store.certification = "",
    new_store.ownerName = "",
    new_store.tag = "",
    new_store.dailyCount = 0,
    new_store.workingInfo = []

    insert_result = collection.insert_one(new_store.dict())

    if not insert_result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가게를 생성 하는데 실패했습니다. 다시 시도해 주세요"
        )

    return {
        "isCreated": True
    }


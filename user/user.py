from fastapi import APIRouter
from pydantic import BaseModel

from lib.db.pymongo_connect_database import connect_database

router = APIRouter()


class CreateUser(BaseModel):
    userName: str
    phoneNumber: str
    userAddress: str
    userDetailAddress: str
    userEmail: str
    userPostCode: str
    userPassword: str


class ValidateEmail(BaseModel):
    userEmail: str


class ResponseValidateEmail(BaseModel):
    isValidate: bool


@router.put("/signup")
async def create_users(user: CreateUser):
    return user
    # collection = get_database_collection()


@router.put("/signup/email")
async def check_email(user: ValidateEmail):
    client = connect_database()
    existingEmail = client.get_database("dnd").get_collection("users").find_one({"userEmail": user.userEmail})

    if (existingEmail):
        client.close()
        print(existingEmail)
        return {"isValidate": False}

    client.close()
    print(existingEmail)
    return {"isValidate": True}

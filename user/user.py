from fastapi import APIRouter
from pydantic import BaseModel

from lib.db.pymongo_connect_database import connect_database
from lib.hash.hash import hashPassword, comparePassword

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


class Signin(BaseModel):
    userEmail: str
    userPassword: str


@router.post("/signup")
async def create_users(user: CreateUser):
    if not user.userName or not user.userPassword:
        return {"message": "Not Valid Input"}

    hashedPassword = hashPassword(user.userPassword)

    client = connect_database()
    if not client:
        return {"message": "Can't connect to database."}

    insertResult = client.get_database("dnd").get_collection("users").insert_one({
        "userName": user.userName,
        "phoneNumber": user.phoneNumber,
        "userAddress": user.userAddress,
        "userDetailAddress": user.userDetailAddress,
        "userEmail": user.userEmail,
        "userPostCode": user.userPostCode,
        "userPassword": hashedPassword
    })
    client.close()

    if insertResult.acknowledged:
        return {"message": "Successfully create user!", "created": True}
    else:
        return {"message": "Fail to create user...", "created": False}


@router.post("/signup/email")
async def check_email(user: ValidateEmail):
    print("get request")
    client = connect_database()

    existingEmail = client.get_database("dnd").get_collection("users").find_one({"userEmail": user.userEmail})

    if (existingEmail):
        client.close()
        print(existingEmail)
        return {"isValid": False}

    client.close()
    print(existingEmail)
    return {"isValid": True}


@router.post("/signin")
async def signin(user: Signin):
    client = connect_database()

    savedUser = client.get_database("dnd").get_collection("users").find_one({"userEmail": user.userEmail})

    isValidPassword = comparePassword(user.userPassword, savedUser["userPassword"])

    if isValidPassword:
        return {"message": "Valid password", "isValid": True}
    else:
        return {"message": "Password is wrong", "isValid": False}

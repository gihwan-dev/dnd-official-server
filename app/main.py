from datetime import datetime

import schedule
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.lib.db.pymongo_connect_database import connect_database
from app.model.store import Daily
from app.order.order import router as order_router
from app.store.store import router as store_router
from app.user.user import router as user_router

app = FastAPI()


# 매 정각마다 dailyCount 초기화 및 total 초기화
# dailyCount를 amount에 total을 total에 할당하고 date에 오늘 날짜를 넣어 years에 month 안에 넣어줘야함.
def initialize_day():
    client = connect_database()
    collections = client.get_database("dnd").get_collection("stores")
    stores = collections.find()
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    for store in stores:
        new_data = Daily(
            date=day,
            total=store["total"],
            amount=store["dailyCount"]
        )
        for store_year in stores["years"]:
            if store_year["year"] == year:
                for store_month in store_year["month_list"]:
                    if store_month["month"] == month:
                        store_month["day_list"].append(new_data.dict())
        collections.update_one({"storeId": store["storeId"]}, {"$set": {
            "total": 0,
            "dailyCount": 0,
            "years": store["years"]
        }})
    client.close()


schedule.every().day.at("00:00").do(initialize_day)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.7:5173",
    "http://127.0.0.7:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def greeting():
    return {"message": "Hello World"}


app.include_router(user_router, prefix="/user")
app.include_router(order_router, prefix="/order")
app.include_router(store_router, prefix="/store")

if __name__ == '__main__':
    uvicorn.run("app.main", host="0.0.0.0", port=8000, reload=True)

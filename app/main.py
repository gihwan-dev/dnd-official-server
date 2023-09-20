import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.order.order import router as order_router
from app.store.store import router as store_router
from app.user.user import router as user_router
from app.robot.main import router as robot_router

app = FastAPI()

# 매 정각마다 dailyCount 초기화 및 total 초기화
# dailyCount를 amount에 total을 total에 할당하고 date에 오늘 날짜를 넣어 years에 month 안에 넣어줘야함.
# def initialize_day():
#     client = connect_database()
#     collections = client.get_database("dnd").get_collection("stores")
#     stores = collections.find()
#     now = datetime.now()
#     year = now.year
#     month = now.month
#     day = now.day
#
#     for store in stores:
#         new_data = Daily(
#             date=day,
#             total=store["total"],
#             amount=store["dailyCount"]
#         )
#         for store_year in stores["years"]:
#             if store_year["year"] == year:
#                 for store_month in store_year["month_list"]:
#                     if store_month["month"] == month:
#                         store_month["day_list"].append(new_data.dict())
#         collections.update_one({"storeId": store["storeId"]}, {"$set": {
#             "total": 0,
#             "dailyCount": 0,
#             "years": store["years"]
#         }})
#     client.close()
#
#
# schedule.every().day.at("00:00").do(initialize_day)

origins = [
    "http://localhost:5173",
    "http://127.0.0.7:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
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
app.include_router(robot_router, prefix="/robot")

if __name__ == '__main__':
    uvicorn.run("app.main", host="0.0.0.0", port=8000, reload=True)

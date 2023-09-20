from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from app.lib.db.pymongo_connect_database import connect_database


router = APIRouter()


class UpdateRobotState(BaseModel):
    temp: int
    lat: int
    long: int


@router.post("/")
async def update_robot_state(update_body: UpdateRobotState):
    client = connect_database()
    client.get_database("dnd").get_collection("robot").insert_one(update_body.dict())
    client.close()
    return {"message": "success"}


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # 클라이언트의 웹소켓 연결 요청을 수락합니다.
    while True:
        data = await websocket.receive_text()  # 클라이언트로부터 데이터를 수신합니다.
        print(f"Received data: {data}")  # 수신된 데이터를 출력합니다.

        # 필요한 로직을 여기에 추가합니다. 예를 들어, 로봇 제어 명령을 처리하는 등의 작업을 수행할 수 있습니다.

        await websocket.send_text(f"Message text was: {data}")  # 클라이언트에게 응답을 전송합니다.


@router.get("/")
async def get_robot_data():
    client = connect_database()
    data = client.get_database("dnd").get_collection("robot").find()
    return {"temp": data[0]["temp"], "lat": data[0]["lat"], "long": data[0]["long"]}

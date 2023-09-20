from pydantic import BaseModel


class Robot(BaseModel):
    temp: int
    lat: int
    long: int

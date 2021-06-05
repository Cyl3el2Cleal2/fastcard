from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Game(BaseModel):
    player: str
    map: List[int]
    picked: List[int] = [0] * 12
    picked_count: int = 0
    last_pick: int = -1


class GameCreateBody(BaseModel):
    player: str


class GameUpdateBody(BaseModel):
    id: str
    player: str
    pick: int


class PickCardResponse(BaseModel):
    message: str
    message_type: int
    data: Optional[Game]

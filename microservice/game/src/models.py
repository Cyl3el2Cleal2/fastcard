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


class GameShow(BaseModel):
    id: str
    player: str
    picked: List[int]
    picked_count: int
    last_pick: int

    class Config:
        schema_extra = {
            "example": {
                "id": "60bc8b3d39292d1233c04c99",
                "player": "abc",
                "picked": [
                    0,
                    3,
                    0,
                    4,
                    4,
                    0,
                    0,
                    0,
                    5,
                    5,
                    2,
                    2
                ],
                "picked_count": 13,
                "last_pick": 2
            }
        }


class GameCreateBody(BaseModel):
    player: str

    class Config:
        schema_extra = {
            "example": {
                "player": "abc"
            }
        }


class GameUpdateBody(BaseModel):
    id: str
    player: str
    pick: int

    class Config:
        schema_extra = {
            "example": {
                "id": "60bbcad1cdb743860c726e2a",
                "player": "abc",
                "pick": 7
            }
        }


class PickCardResponse(BaseModel):
    message: str
    message_type: int
    data: Optional[dict]

    class Config:
        schema_extra = {
            "example": {
                "message": "Congrate",
                "message_type": 8,
                "data": {
                    "player": "abc",
                    "picked": [
                        0,
                        3,
                        0,
                        4,
                        4,
                        0,
                        0,
                        0,
                        5,
                        5,
                        2,
                        2
                    ],
                    "picked_count": 13,
                    "last_pick": 2
                }
            }
        }

from pydantic import BaseModel
from typing import List
import datetime

class Game(BaseModel):
  id: int
  player: str
  map: List[int]
  picked: List[int]
  picked_count: int
  created_at: datetime = datetime.datetime.now()
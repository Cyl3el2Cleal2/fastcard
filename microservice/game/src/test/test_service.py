from hashlib import new
import os, sys
import pytest
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
 
from service import GameService
from db import connect_db
from mq import MQ


gs = GameService()


@pytest.mark.asyncio
async def test_boardcast():
 await connect_db()
 await MQ().create_master()
 result = await gs.boardcast_winner("abc" , 2)
 assert result == True

@pytest.mark.asyncio
async def test_random_map():
  map = gs.random_map()
  assert len(map) == 12
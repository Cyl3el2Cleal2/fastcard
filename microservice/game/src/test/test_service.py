import os
import sys
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from service import GameService
from models import Game
import db

gs = GameService()

@pytest.fixture
def mock_db_and_mq(mocker):
    db_mock = {}

    async def insert_one(data):
        game_id = ObjectId()
        data['_id'] = game_id
        db_mock[game_id] = data
        return MagicMock(inserted_id=game_id)

    async def find_one(query):
        if '_id' in query:
            game_id = query['_id']
            if isinstance(game_id, str):
                game_id = ObjectId(game_id)
            return db_mock.get(game_id)
        return None

    async def update_one(query, update_data):
        game_id = query['_id']
        if isinstance(game_id, str):
            game_id = ObjectId(game_id)
        if game_id in db_mock:
            db_mock[game_id].update(update_data['$set'])
        return MagicMock(modified_count=1)

    mock_collection = MagicMock()
    mock_collection.insert_one = AsyncMock(side_effect=insert_one)
    mock_collection.find_one = AsyncMock(side_effect=find_one)
    mock_collection.update_one = AsyncMock(side_effect=update_one)

    mocker.patch.object(db, 'game_collection', mock_collection)
    mocker.patch.object(db, 'connect_db', AsyncMock())

    # Mock MQ
    mock_master = MagicMock()
    mock_master.create_task = AsyncMock()
    mocker.patch("mq.MQ.get_master", return_value=mock_master)
    mocker.patch("mq.MQ.create_master", AsyncMock())

    return db_mock, mock_collection

@pytest.fixture
async def setup_game(mock_db_and_mq):
    db_mock, _ = mock_db_and_mq
    db_mock.clear()
    game = Game(player="test_player", map=[1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6])
    saved_game = await gs.save_game(game.dict())
    return saved_game['id']


@pytest.mark.asyncio
async def test_random_map():
    map_ = gs.random_map()
    assert len(map_) == 12
    assert sum(map_) > 0

@pytest.mark.asyncio
async def test_pick_first_card(setup_game):
    game_id = setup_game
    game_state = await gs.pick_card(game_id, 1)
    assert game_state["picked_count"] == 1
    assert game_state["last_pick"] == 1
    assert game_state["picked"][0] == 1

@pytest.mark.asyncio
async def test_pick_second_card_correct(setup_game):
    game_id = setup_game
    await gs.pick_card(game_id, 1)
    game_state = await gs.pick_card(game_id, 2)
    assert game_state["picked_count"] == 2
    assert game_state["last_pick"] == -1
    assert game_state["picked"][0] == 1
    assert game_state["picked"][1] == 1

@pytest.mark.asyncio
async def test_pick_second_card_incorrect(setup_game):
    game_id = setup_game
    await gs.pick_card(game_id, 1)
    game_state = await gs.pick_card(game_id, 3)
    assert game_state["picked_count"] == 2
    assert game_state["last_pick"] == -1
    assert game_state["picked"][0] == 0
    assert game_state["picked"][2] == 0

@pytest.mark.asyncio
async def test_pick_card_out_of_range(setup_game):
    game_id = setup_game
    with pytest.raises(HTTPException) as excinfo:
        await gs.pick_card(game_id, 13)
    assert excinfo.value.status_code == 400

@pytest.mark.asyncio
async def test_pick_same_card(setup_game):
    game_id = setup_game
    await gs.pick_card(game_id, 1)
    with pytest.raises(HTTPException) as excinfo:
        await gs.pick_card(game_id, 1)
    assert excinfo.value.status_code == 400

@pytest.mark.asyncio
async def test_pick_opened_card(setup_game):
    game_id = setup_game
    await gs.pick_card(game_id, 1)
    await gs.pick_card(game_id, 2)
    with pytest.raises(HTTPException) as excinfo:
        await gs.pick_card(game_id, 1)
    assert excinfo.value.status_code == 409

@pytest.mark.asyncio
async def test_game_over(setup_game, mock_db_and_mq):
    db_mock, _ = mock_db_and_mq
    game_id = setup_game
    game_obj_id = ObjectId(game_id)
    db_mock[game_obj_id]["picked"] = db_mock[game_obj_id]["map"].copy()

    with pytest.raises(HTTPException) as excinfo:
        await gs.pick_card(game_id, 1)
    assert excinfo.value.status_code == 409

@pytest.mark.asyncio
async def test_win_game(setup_game):
    game_id = setup_game
    await gs.pick_card(game_id, 1)
    await gs.pick_card(game_id, 2)
    await gs.pick_card(game_id, 3)
    await gs.pick_card(game_id, 4)
    await gs.pick_card(game_id, 5)
    await gs.pick_card(game_id, 6)
    await gs.pick_card(game_id, 7)
    await gs.pick_card(game_id, 8)
    await gs.pick_card(game_id, 9)
    await gs.pick_card(game_id, 10)
    await gs.pick_card(game_id, 11)
    game_state = await gs.pick_card(game_id, 12)
    assert game_state["picked"] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
    assert game_state["picked_count"] == 12
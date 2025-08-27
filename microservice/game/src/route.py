from fastapi import APIRouter, Body, status, HTTPException
from models import GameShow, GameCreateBody, PickCardBody
from service import GameService
from fastapi.encoders import jsonable_encoder

router = APIRouter()

gameservice = GameService()


@router.get('/games/{game_id}', response_model=GameShow)
async def get_game(game_id: str):
    game = await gameservice.get_game(game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"Not found game id : {game_id}")
    return game


@router.post('/games', status_code= 201, response_model=GameShow)
async def create_game(game: GameCreateBody = Body(...)):
    new_game = gameservice.create_game(game.player)
    result = await gameservice.save_game(jsonable_encoder(new_game))
    return result


@router.post('/games/{game_id}/pick', response_model=GameShow)
async def pick_card(game_id: str, data: PickCardBody = Body(...)):
    updated_game = await gameservice.pick_card(game_id, data.pick)
    return updated_game

@router.get('/top_score')
async def top_score():
    return await gameservice.get_top_score()

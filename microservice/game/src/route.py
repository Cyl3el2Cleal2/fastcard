from fastapi import APIRouter, Body, status, HTTPException
from models import GameShow, GameCreateBody, GameUpdateBody, PickCardResponse
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


@router.put('/games', response_model=PickCardResponse)
async def pick_card(data: GameUpdateBody = Body(...)):
    updating = await gameservice.pick_card(data)
    return updating

@router.get('/top_score')
async def top_score():
    return await gameservice.get_top_score()

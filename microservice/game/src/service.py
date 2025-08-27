import random
from typing import List
from fastapi import HTTPException, status
from models import Game
from db import (retrieve_game, add_game, update_game, find_top_score)
from mq import MQ
class GameService:
    _top_score = None
    def random_map(self) -> List[int]:
        """ create map template
        """
        all_card = list(range(1, 7)) * 2
        map = [0] * 12
        for i in range(len(map)):
            random_index = random.randint(0, len(all_card)-1)
            card = all_card[random_index]
            map[i] = card
            all_card.remove(card)
        return map

    def create_game(self, player_name: str) -> Game:
        map = self.random_map()
        new_game = Game(player=player_name, map=map)
        return new_game

    def show_game(self, game: Game) -> dict:
        return {
            "id": str(game["_id"]),
            "player": str(game["player"]),
            "picked": game["picked"],
            "picked_count": int(game["picked_count"]),
            "last_pick": int(game["last_pick"])
        }

    async def get_top_score(self):
        # Find finished game
        top_score_doc = await find_top_score()
        if top_score_doc:
            top_score = top_score_doc["picked_count"]
            return {"score": top_score}
        return {"score": None}

    async def save_game(self, game: Game) -> Game:
        save = await add_game(game)
        return save

    async def get_game(self, id: str) -> Game:
        game = await retrieve_game(id)
        return game

    async def pick_card(self, game_id: str, pick: int) -> dict:
        game = await self.get_game(game_id)
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id {game_id} not found")

        if game["picked"] == game["map"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This game is over.")

        if pick <= 0 or pick > 12:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pick must be in range 1 - 12.")

        if game["last_pick"] == pick:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Don't pick the same card as the previous pick.")

        if game["picked"][pick-1] != 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Card number {pick} has already been opened.")

        # Opening first card of two
        if game["last_pick"] == -1:
            game["picked"][pick-1] = game["map"][pick-1]
            game["picked_count"] += 1
            game["last_pick"] = pick
            updated = await update_game(game_id, game)
            return self.show_game(updated)

        # Opening second card
        # Correct match
        if game["picked"][game["last_pick"]-1] == game["map"][pick-1]:
            game["picked"][pick-1] = game["map"][pick-1]
            game["last_pick"] = -1
            game["picked_count"] += 1

            # Win game
            if game["picked"] == game["map"]:
                score = game["picked_count"]
                player = game["player"]
                await self.boardcast_winner(player, score)

            updated = await update_game(game_id, game)
            return self.show_game(updated)

        # Incorrect match
        else: # game["picked"][game["last_pick"]-1] != game["map"][pick-1]
            # then hide the previous card
            game["picked"][game["last_pick"]-1] = 0
            game["picked_count"] += 1
            game["last_pick"] = -1
            updated = await update_game(game_id, game)
            return self.show_game(updated)

    async def boardcast_winner(self, player: str, score: int):
        # send task to rank service if score is greater than current state
        top_score_data = await self.get_top_score()
        top_score = top_score_data["score"]

        if top_score is None or score < top_score:
            await MQ.get_master().create_task("ranking", kwargs=dict(score=score))
            return True
        return False
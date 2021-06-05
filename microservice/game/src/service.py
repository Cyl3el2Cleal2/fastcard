import random
from typing import List
from models import Game, PickCardResponse, GameUpdateBody
from db import (retrieve_game, add_game, update_game)


class GameService:
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

    async def save_game(self, game: Game) -> Game:
        save = await add_game(game)
        return save

    async def get_game(self, id: str) -> Game:
        game = await retrieve_game(id)
        return game

    async def pick_card(self, data: GameUpdateBody) -> PickCardResponse:
        pick = data.pick
        game = await self.get_game(data.id)
        print(data, game)
        if game:
            if pick <= 0 or pick > 12:
                # Pick out of range
                return {'pick must in range 1 - 12.'}
            if game["last_pick"] == pick:
                # pick same card as previous pick
                # return {'dont pick same card as previous pick'}
                return PickCardResponse(message="dont pick same card as previous pick.", message_type=1, data=self.show_game(game))
            if game["picked"][pick-1] != 0:
                # return {'this card was open'}
                return PickCardResponse(message=f"this card number {pick} was open.", message_type=2, data=self.show_game(game))
            if game["map"] == game["picked"]:
                return {'this game is over'}

            # openning first card of two
            if game["last_pick"] == -1:
                game["picked"][pick-1] = game["map"][pick-1]
                game["picked_count"] += 1
                game["last_pick"] = pick
                updated = await update_game(data.id, game)
                # return self.show_game(updated)
                return PickCardResponse(message=f"OK, Pick a next card to matching.", message_type=3, data=self.show_game(game))

            # openning second card of two and pick correct card!
            if game["picked"][game["last_pick"]-1] == game["map"][pick-1]:
                # then show the picking card
                game["picked"][pick-1] = game["map"][pick-1]
                # reset the last_pick value to -1
                game["last_pick"] = -1
                # count picking
                game["picked_count"] += 1
                updated = await update_game(data.id, game)
                # return self.show_game(updated)
                return PickCardResponse(message=f"Nice, Find next couple.", message_type=4, data=self.show_game(updated))

            # openning second card of two and pick wrong card!
            if game["picked"][game["last_pick"]-1] != game["map"][pick-1]:
                # keep old_picked for show to user
                old_state = [*game["picked"]]
                old_state[pick-1] = game["map"][pick-1] # open the pick card


                # then hide the previous card
                game["picked"][game["last_pick"]-1] = 0
                # count picking
                game["picked_count"] += 1
                # reset the last_pick value to -1
                game["last_pick"] = -1
                updated = await update_game(data.id, game)
                data = self.show_game(updated)
                data["old_picked"] = old_state
                return PickCardResponse(message=f"Unlucky, Please remember card position.", message_type=5, data=data)

        return PickCardResponse(message="Not found", message_type=0)


if __name__ == "__main__":
    game = GameService()
    map = game.random_map()
    print(map)
    print(game.create_game())

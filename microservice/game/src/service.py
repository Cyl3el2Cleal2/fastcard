import random
from model import Game

class GameService:
    def random_map(self) -> list[int]:
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

    def match_card(self, pick: int, last_pick: int, map: list[int]) -> bool:
        """
        when player pick a card this fuction will verify matching
        """
        if pick != last_pick and map[pick] == map[last_pick]:
            return True
        return False
    
    def create_game(self) -> Game:
      new_game = Game()
      return new_game


if __name__ == "__main__":
    game = GameService()
    map = game.random_map()
    print(map)
    print(game.create_game())

from globals import GameState
from pydantic import BaseModel
from typing import List, Optional


class Player(BaseModel):
    id: int
    name: str
    elo: int = 0

    def __hash__(self):
        return hash(self.id)


class Game(BaseModel):
    id: int
    state: GameState = GameState.UNPLAYED
    players: List[Player] = []
    winner: Optional[Player] = None

    def __hash__(self):
        return hash(self.id)
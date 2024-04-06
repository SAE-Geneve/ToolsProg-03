from typing import List
from pydantic import BaseModel
from globals import GameState


class Player(BaseModel):
    id: int | None = None
    name: str | None = None
    elo: int = 0


class Game(BaseModel):
    id: int | None = None
    state: int = GameState.UNPLAYED.value
    players: List[Player] = []
    winner: Player | None = None


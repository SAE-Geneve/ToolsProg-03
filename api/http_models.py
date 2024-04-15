from typing import List
from pydantic import BaseModel
from globals import GameState


class NewPlayer(BaseModel):
    name: str
    elo: int = 0


class ExistingPlayer(BaseModel):
    id: int
    name: str
    elo: int


class Game(BaseModel):
    id: int | None = None
    state: GameState = GameState.UNPLAYED
    players: List[ExistingPlayer] = []
    winner: ExistingPlayer | None = None


from enum import IntEnum, auto, unique


@unique
class GameState(IntEnum):
    UNPLAYED = 0
    FINISHED = 10
    PLAYING = 11
    ABORTED = 100


@unique
class GameResult(IntEnum):
    UNPLAYED = auto()
    PLAYING = auto()
    WON = auto()
    LOST = auto()
    ABORTED = auto()


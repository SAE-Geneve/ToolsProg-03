from enum import IntEnum, unique


@unique
class GameState(IntEnum):
    UNPLAYED = 0
    PLAYING = 1
    FINISHED = 2
    ABORTED = 3


@unique
class GameResult(IntEnum):
    UNPLAYED = 0
    PLAYING = 1
    WON = 2
    LOST = 3
    ABORTED = 4


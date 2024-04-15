from enum import IntEnum, unique


@unique
class GameState(IntEnum):
    UNPLAYED = 0
    FINISHED = 10
    PLAYING = 11
    ABORTED = 100


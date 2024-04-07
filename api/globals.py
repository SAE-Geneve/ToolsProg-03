from enum import IntEnum, auto, unique


@unique
class GameState(IntEnum):
    UNPLAYED = auto()
    PLAYING = auto()
    FINISHED = auto()
    ABORTED = auto()


@unique
class GameResult(IntEnum):
    UNPLAYED = auto()
    PLAYING = auto()
    WON = auto()
    LOST = auto()
    ABORTED = auto()


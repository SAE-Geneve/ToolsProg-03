from PySide2 import QtCore
from enum import IntEnum, unique


class Role(IntEnum):
    WHOLE_DATA_ROLE = QtCore.Qt.UserRole + 1
    ID_ROLE = QtCore.Qt.UserRole + 2


@unique
class GameState(IntEnum):
    UNPLAYED = 0
    FINISHED = 10
    PLAYING = 11
    ABORTED = 100


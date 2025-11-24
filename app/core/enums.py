from enum import Enum

class SpinStatus(Enum):
    SUCCESS = "success"
    ALREADY_SPUN = "already_spun"
    NO_PRIZES = "no_prizes"
    PLAYER_NOT_FOUND = "player_not_found"
    ERROR = "error"
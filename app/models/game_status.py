from enum import Enum

class GameStatus(Enum):
    WAITING_FOR_CHOICE = "waiting for player choice of action"
    PLACING_DRAW = "placing drawn card"
    FINAL_ASSIGNMENT = "making final assignments"
    COMPLETED = "completed"
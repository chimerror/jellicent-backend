from enum import Enum

class GameChoice(str, Enum):
    DRAW_CARD = "draw-card"
    TAKE_PILE = "take-pile"

GAME_CHOICE_VALUES = [value for name, value in GameChoice.__members__.items()]
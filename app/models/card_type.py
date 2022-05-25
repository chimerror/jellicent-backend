from enum import Enum

class CardType(str, Enum):
    WILD = "wild"
    PLUS_TWO = "plus two"
    RAT = "rat"
    RABBIT = "rabbit"
    SNAKE = "snake"
    SHEEP = "sheep"
    MONKEY = "monkey"
    CHICKEN = "chicken"
    DOG = "dog"

    def is_special_card(self):
        return self in SPECIAL_CARDS

    def is_player_card(self):
        return self in PLAYER_CARDS

SPECIAL_CARDS = { CardType.WILD, CardType.PLUS_TWO }

PLAYER_CARDS = { 
    CardType.RAT,
    CardType.RABBIT,
    CardType.SNAKE,
    CardType.SHEEP,
    CardType.MONKEY,
    CardType.CHICKEN,
    CardType.DOG
}

CARD_COUNTS = {
    CardType.WILD: 3,
    CardType.PLUS_TWO: 10,
    CardType.RAT: 9,
    CardType.RABBIT: 9,
    CardType.SNAKE: 9,
    CardType.SHEEP: 9,
    CardType.MONKEY: 9,
    CardType.CHICKEN: 9,
    CardType.DOG: 9,
}
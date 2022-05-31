from app import db
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .card_type import CardType

class GamePlayer(db.Model):
    __tablename__ = "games_x_players"
    game_id = db.Column(
        UUID(as_uuid = True), db.ForeignKey("games.id"), primary_key = True)
    game = db.relationship("Game", back_populates = "players")
    player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), primary_key = True)
    player = db.relationship("Player", back_populates = "games")
    player_index = db.Column(db.SmallInteger, nullable = False)
    starting_card = db.Column(db.Enum(CardType), nullable = False)
    took_this_round = db.Column(db.Boolean, nullable = False, default = False)
    wild_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    wild_assignments = db.Column(JSONB, nullable = True)
    plus_two_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    rat_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    rabbit_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    snake_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    sheep_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    monkey_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    chicken_count = db.Column(db.SmallInteger, nullable = False, default = 0)
    dog_count = db.Column(db.SmallInteger, nullable = False, default = 0)

    def get_count_by_card_type(self, card_type):
        if card_type == CardType.RAT:
            return self.rat_count
        elif card_type == CardType.RABBIT:
            return self.rabbit_count
        elif card_type == CardType.SNAKE:
            return self.snake_count
        elif card_type == CardType.SHEEP:
            return self.sheep_count
        elif card_type == CardType.MONKEY:
            return self.monkey_count
        elif card_type == CardType.CHICKEN:
            return self.chicken_count
        elif card_type == CardType.DOG:
            return self.dog_count
        elif card_type == CardType.WILD:
            return self.wild_count
        elif card_type == CardType.PLUS_TWO:
            return self.plus_two_count
        else:
            raise ValueError(f"Unknown card type {card_type} passed to get_count_by_card_type")

    def set_count_by_card_type(self, card_type, new_count):
        if card_type == CardType.RAT:
            self.rat_count = new_count
        elif card_type == CardType.RABBIT:
            self.rabbit_count = new_count
        elif card_type == CardType.SNAKE:
            self.snake_count = new_count
        elif card_type == CardType.SHEEP:
            self.sheep_count = new_count
        elif card_type == CardType.MONKEY:
            self.monkey_count = new_count
        elif card_type == CardType.CHICKEN:
            self.chicken_count = new_count
        elif card_type == CardType.DOG:
            self.dog_count = new_count
        elif card_type == CardType.WILD:
            self.wild_count = new_count
        elif card_type == CardType.PLUS_TWO:
            self.plus_two_count = new_count
        else:
            raise ValueError(f"Unknown card type {card_type} passed to set_count_by_card_type")

    def increment_count_by_card_type(self, card_type):
        self.set_count_by_card_type(
            card_type,
            self.get_count_by_card_type(card_type) + 1)

    def add_wild_assignments(self, new_assignments):
        if self.wild_assignments:
            for wild_assignment in new_assignments:
                self.wild_assignments.apped(wild_assignment)
        else:
            self.wild_assignments = new_assignments
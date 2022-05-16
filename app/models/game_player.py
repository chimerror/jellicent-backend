from app import db
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .card_type import CardType

class GamePlayer(db.Model):
    __tablename__ = "games_x_players"
    game_id = db.Column(
        UUID(as_uuid = True), db.ForeignKey("games.id"), primary_key = True)
    player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), primary_key = True)
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
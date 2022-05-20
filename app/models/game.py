from app import db
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
from .game_status import GameStatus

class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(
        UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    status = db.Column(db.Enum(GameStatus), nullable = False)
    players = db.relationship("GamePlayer", back_populates = "game")
    active_player_index = db.Column(db.SmallInteger, nullable = False)
    use_advanced_scoring = db.Column(db.Boolean, nullable = False)
    assign_wilds_on_take = db.Column(db.Boolean, nullable = False)
    deck = db.Column(JSONB, nullable = False)
    current_deck_index = db.Column(db.SmallInteger, nullable = False)
    pile_one = db.Column(JSONB)
    pile_two = db.Column(JSONB)
    pile_three = db.Column(JSONB)
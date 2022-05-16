from app.models.card_type import CardType
from app.models.game_status import GameStatus
from app.models.game import Game
from app.models.game_player import GamePlayer
from app.models.player import Player
from flask import Blueprint

games_bp = Blueprint("games", __name__, url_prefix = "/games")

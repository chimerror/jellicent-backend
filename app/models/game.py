from app import db
from flask import make_response, abort
from sqlalchemy.dialects.postgresql import JSONB, UUID
import random
import uuid
from .card_type import CardType, CARD_COUNTS, PLAYER_CARDS
from .game_player import GamePlayer
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
    removed_card = db.Column(db.Enum(CardType))
    deck = db.Column(JSONB, nullable = False)
    current_deck_index = db.Column(db.SmallInteger, nullable = False)
    pile_one = db.Column(JSONB)
    pile_two = db.Column(JSONB)
    pile_three = db.Column(JSONB)
    pile_four = db.Column(JSONB)
    pile_five = db.Column(JSONB)

    def __init__(
        self,
        players,
        use_advanced_scoring,
        assign_wilds_on_take,
        random_seed = None):

        random.seed(random_seed)
        self.status = GameStatus.WAITING_FOR_CHOICE
        self.active_player_index = 0
        self.use_advanced_scoring = use_advanced_scoring
        self.assign_wilds_on_take = assign_wilds_on_take

        self.removed_card = None
        available_player_cards = list(PLAYER_CARDS)
        player_count = len(players)
        if player_count == 3:
            self.removed_card = random.choice(available_player_cards)
            available_player_cards.remove(self.removed_card)
        player_starting_cards = \
            random.sample(available_player_cards, player_count)
        player_indicies = list(range(player_count))
        random.shuffle(player_indicies)

        for current_index in range(player_count):
            current_player = players[current_index]
            current_starting_card = player_starting_cards[current_index]
            game_player = GamePlayer(
                player_index = player_indicies[current_index],
                starting_card = current_starting_card)
            game_player.set_count_by_card_type(current_starting_card, 1)
            game_player.player = current_player
            self.players.append(game_player)

        deck = []
        for name, member in CardType.__members__.items():
            if member != self.removed_card:
                cards_needed = CARD_COUNTS[member]
                if member in player_starting_cards:
                    cards_needed = cards_needed - 1
                for i in range(cards_needed):
                    deck.append(name)
        random.shuffle(deck)
        self.deck = deck
        self.current_deck_index = 0

        self.pile_one = []
        self.pile_two = []
        self.pile_three = []
        self.pile_four = [] if player_count >= 4 else None
        self.pile_five = [] if player_count == 5 else None

def validate_game_id(game_id, game_not_found_status_code = 404):
    try:
        uuid_game_id = uuid.UUID(game_id)
    except:
        abort(make_response(
            {"message": f"'{game_id}' is not a valid game ID"}, 400))

    game = Game.query.get(game_id)

    if not game:
        abort(make_response(
            {"message": f"No game with ID {game_id} was found"},
            game_not_found_status_code))

    return game
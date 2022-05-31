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
        self.reset_piles()

    def get_player_count(self):
        return len(self.players)

    def get_active_player(self):
        for player in self.players:
            if player.player_index == self.active_player_index:
                return player
        raise RuntimeError("Could not find active player in game!")

    def move_to_next_player(self):
        while True:
            self.active_player_index += 1
            if self.active_player_index >= len(self.players):
                self.active_player_index = 0
            if not self.players[self.active_player_index].took_this_round:
                break

    def get_cards_left(self):
        return len(self.deck) - self.current_deck_index

    def is_last_round(self):
        return self.get_cards_left() <= 15

    def get_available_piles(self):
        piles = []
        if not self.pile_one is None:
            piles.append(self.pile_one)
        if not self.pile_two is None:
            piles.append(self.pile_two)
        if not self.pile_three is None:
            piles.append(self.pile_three)
        if not self.pile_four is None:
            piles.append(self.pile_four)
        if not self.pile_five is None:
            piles.append(self.pile_five)
        return piles

    def take_pile(self, pile_index_to_take, wild_assignments = None):
        available_piles = self.get_available_piles()
        taken_pile = available_piles.pop(pile_index_to_take)

        active_player = self.get_active_player()
        for card_string in taken_pile:
            card_type = CardType(card_string)
            active_player.increment_count_by_card_type(card_type)
        if wild_assignments:
            active_player.add_wild_assignments(wild_assignments)
        active_player.took_this_round = True

        piles_left = len(available_piles)
        if piles_left > 0:
            self.pile_one = available_piles[0] if piles_left >= 1 else None
            self.pile_two = available_piles[1] if piles_left >= 2 else None
            self.pile_three = available_piles[2] if piles_left >= 3 else None
            self.pile_four = available_piles[3] if piles_left >= 4 else None
            self.pile_five = available_piles[4] if piles_left >= 5 else None
            self.move_to_next_player()
            self.status = GameStatus.WAITING_FOR_CHOICE
        elif self.is_last_round():
            self.active_player_index = 0
            self.status = GameStatus.FINAL_ASSIGNMENT
        else:
            self.reset_piles()
            for player in self.players:
                player.took_this_round = False
            self.status = GameStatus.WAITING_FOR_CHOICE

    def reset_piles(self):
        player_count = self.get_player_count()
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
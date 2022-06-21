from app import db
from app.models.card_type import CardType, PLAYER_CARDS
from app.models.game import Game, validate_game_id
from app.models.game_choice import GameChoice, GAME_CHOICE_VALUES
from app.models.game_status import GameStatus
from app.models.player import validate_player_id
from flask import Blueprint, make_response, abort, request
from utils.utils import to_bool

games_bp = Blueprint("games", __name__, url_prefix = "/games")

@games_bp.route("", methods = ["POST"])
def create_game():
    request_body = request.get_json()

    if not "player-ids" in request_body:
        abort(make_response(
            { "message": "Missing required field 'player-ids'" }, 400))

    player_ids = request_body["player-ids"]
    BAD_PLAYER_ID_LIST_MESSAGE = \
        "Field 'player-ids' must be a list of valid existing player ids with 3 to 5 elements."
    if not isinstance(player_ids, list):
        abort(make_response({ "message": BAD_PLAYER_ID_LIST_MESSAGE } , 400))

    player_count = len(player_ids)
    if player_count < 3 or player_count > 5:
        abort(make_response({ "message": BAD_PLAYER_ID_LIST_MESSAGE } , 400))

    players = []
    for player_id in player_ids:
        player = validate_player_id(player_id, 400)

        for existing_player in players:
            if existing_player.id == player.id:
                abort(make_response(
                    {"message": f"Player ID {player_id} was duplicated in field 'player-ids'"},
                    400))

        players.append(player)

    use_advanced_scoring = False
    if "use-advanced-scoring" in request_body:
        use_advanced_scoring = to_bool(request_body["use-advanced-scoring"])
    
    assign_wilds_on_take = False
    if "assign-wilds-on-take" in request_body:
        assign_wilds_on_take = to_bool(request_body["assign-wilds-on-take"])

    random_seed = None
    if "random-seed" in request_body:
        request_seed = request_body["random-seed"]
        try:
            random_seed = int(request_seed)
        except:
            abort(make_response(
                {"message": f"'{request_seed}' is not an integer"}, 400))

    new_game = Game(
        players, use_advanced_scoring, assign_wilds_on_take, random_seed)
    db.session.add(new_game)
    db.session.commit()

    db.session.refresh(new_game, ["id"])
    return make_response(
        f"Game with ID {new_game.id} successfully created",
        201)

@games_bp.route("/<game_id>", methods = ["GET"])
def get_game_by_id(game_id):
    game = validate_game_id(game_id)
    cards_left = game.get_cards_left()
    is_last_round = game.is_last_round()

    sorted_raw_players = sorted(game.players, key = lambda p: p.player_index)
    response_players = []
    for player in sorted_raw_players:
        response_player = {
            "id": player.player_id,
            "starting-card": player.starting_card,
            "took-this-round": player.took_this_round
        }
        response_hand = {}
        if player.wild_count > 0:
            response_hand["wild"] = player.wild_count
        if player.plus_two_count > 0:
            response_hand["plus-two"] = player.plus_two_count
        if player.rat_count > 0:
            response_hand["rat"] = player.rat_count
        if player.rabbit_count > 0:
            response_hand["rabbit"] = player.rabbit_count
        if player.snake_count > 0:
            response_hand["snake"] = player.snake_count
        if player.sheep_count > 0:
            response_hand["sheep"] = player.sheep_count
        if player.monkey_count > 0:
            response_hand["monkey"] = player.monkey_count
        if player.chicken_count > 0:
            response_hand["chicken"] = player.chicken_count
        if player.dog_count > 0:
            response_hand["dog"] = player.dog_count
        response_player["hand"] = response_hand
        if player.wild_assignments:
            response_player["wild-assignments"] = player.wild_assignments
        response_players.append(response_player)

    response_body = {
        "current-state": game.status,
        "active-player-index": game.active_player_index,
        "use-advanced-scoring": game.use_advanced_scoring,
        "assign-wilds-on-take": game.assign_wilds_on_take,
        "piles": game.get_available_piles(),
        "cards-left": cards_left,
        "last-round": is_last_round,
        "players": response_players
    }
    if game.removed_card:
        response_body["removed-card"] = game.removed_card
    if game.status == GameStatus.WAITING_FOR_CHOICE:
        choices_allowed = []
        for pile in response_body["piles"]:
            pile_card_count = len(pile)
            if not "take-pile" in choices_allowed and pile_card_count > 0:
                choices_allowed.append("take-pile")
            elif not "draw-card" in choices_allowed and pile_card_count < 3:
                choices_allowed.append("draw-card")
        response_body["choices-allowed"] = choices_allowed
    return response_body

@games_bp.route("/<game_id>/make-choice", methods = ["PATCH"])
def make_choice(game_id):
    game = validate_game_id(game_id)

    if game.status != GameStatus.WAITING_FOR_CHOICE:
        abort(make_response(
            {"message": f"Game {game_id} has status '{game.status.value}' not '{GameStatus.WAITING_FOR_CHOICE.value}' and thus cannot accept choices at this time"},
            400))

    request_body = request.get_json()
    if not "choice" in request_body:
        abort(make_response(
            { "message": "Missing required field 'choice'" }, 400))

    choice = request_body["choice"]
    if not choice in GAME_CHOICE_VALUES:
        abort(make_response(
            { "message": f"'{choice}' is not a valid game choice" }, 400))
    else:
        choice = GameChoice(choice)
    
    response_body = {}
    if choice == GameChoice.DRAW_CARD:
        drawn_card = game.draw_card()
        response_body["message"] = "Successfully drew card"
        response_body["drawn-card"] = drawn_card.value
    else:
        pile_index_to_take = validate_pile_to_take(game, request_body)
        wild_assignments = \
            validate_wild_assignments(game, pile_index_to_take, request_body)
        taken_pile = game.take_pile(pile_index_to_take, wild_assignments)
        response_body["message"] = f"Successfully took pile {pile_index_to_take}"
        response_body["taken-pile"] = taken_pile

    db.session.commit()
    return response_body

def validate_pile_to_take(game, request_body):
    if not "pile-to-take" in request_body:
        abort(make_response(
            { "message": "Missing required field for 'take-pile', 'pile-to-take'" },
            400))

    available_piles = game.get_available_piles()
    bad_pile_to_take_message = \
        f"Field 'pile-to-take' must be a non-negative integer from 0 to {len(available_piles)}"
    pile_index_to_take = 0
    try:
        pile_index_to_take = int(request_body["pile-to-take"])
    except:
        abort(make_response(
            { "message": bad_pile_to_take_message }, 400))

    if pile_index_to_take < 0 or pile_index_to_take > len(available_piles) - 1:
        abort(make_response(
            { "message": bad_pile_to_take_message }, 400))

    pile_to_take = available_piles[pile_index_to_take]
    if len(pile_to_take) < 1:
        abort(make_response(
            { "message": f"Cannot take pile {pile_index_to_take} as no cards have been placed in it" }, 400))

    return pile_index_to_take

def validate_wild_assignments(game, pile_index_to_take, request_body):
    available_piles = game.get_available_piles()
    pile_wild_count = 0
    for card_name in available_piles[pile_index_to_take]:
        card = CardType(card_name)
        if card == CardType.WILD:
            pile_wild_count += 1

    wild_assignments = None
    if game.assign_wilds_on_take:
        if pile_wild_count > 0:
            if not "wild-assignments" in request_body:
                abort(make_response(
                    { "message": "Missing required field 'wild-assignments' for taking a pile with wild cards while wild assginment on take is enabled" },
                    400))

            raw_assignments = request_body["wild-assignments"]
            bad_wild_assignments_list_message = \
                f"Field 'wild-assignments' must be a list of player cards with {pile_wild_count} element(s)."
            if not isinstance(raw_assignments, list):
                abort(make_response(
                    { "message": bad_wild_assignments_list_message },
                    400))

            if len(raw_assignments) != pile_wild_count:
                abort(make_response(
                    { "message": bad_wild_assignments_list_message },
                    400))

            wild_assignments = []
            for raw_assignment in raw_assignments:
                try:
                    wild_assignment = CardType(raw_assignment)
                    if not wild_assignment in PLAYER_CARDS:
                            raise ValueError
                    wild_assignments.append(wild_assignment)
                except:
                    abort(make_response(
                        { "message": f"'{raw_assignment}' is not a valid player card for wild assignment" },
                        400))
        elif "wild-assignments" in request_body:
            abort(make_response(
                { "message": "'wild-assginments' field supplied despite no wilds in pile to take"},
                400))
    elif "wild-assignments" in request_body:
        abort(make_response(
            { "message": "'wild-assginments' field supplied despite wild assignment on take being disabled" },
            400))
    
    return wild_assignments

@games_bp.route("/<game_id>/place-draw", methods = ["PATCH"])
def place_draw(game_id):
    game = validate_game_id(game_id)

    if game.status != GameStatus.PLACING_DRAW:
        abort(make_response(
            {"message": f"Game {game_id} has status '{game.status.value}' not '{GameStatus.PLACING_DRAW.value}' and thus cannot accept card placement at this time"},
            400))

    request_body = request.get_json()
    if not "pile-to-place-on" in request_body:
        abort(make_response(
            { "message": "Missing required field 'pile-to-place-on'" }, 400))

    available_piles = game.get_available_piles()
    bad_pile_to_place_on_message = \
        f"Field 'pile-to-place-on' must be a non-negative integer from 0 to {len(available_piles)}"
    pile_index_to_place_on = 0
    try:
        pile_index_to_place_on = int(request_body["pile-to-place-on"])
    except:
        abort(make_response(
            { "message": bad_pile_to_place_on_message }, 400))

    if pile_index_to_place_on < 0 or pile_index_to_place_on > len(available_piles) - 1:
        abort(make_response(
            { "message": bad_pile_to_place_on_message }, 400))

    pile_to_place_on = available_piles[pile_index_to_place_on]
    if len(pile_to_place_on) == 3:
        abort(make_response(
            { "message": f"Cannot place on pile {pile_index_to_place_on} as three cards have already been placed in it, so it's full" }, 400))

    placed_card = game.get_next_card()
    game.place_on_pile(pile_index_to_place_on)
    db.session.commit()
    return {
        "message": f"Successfully placed {placed_card} on pile {pile_index_to_place_on}",
        "card_placed": placed_card
    }
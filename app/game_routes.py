from app import db
from app.models.game import Game, validate_game_id
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
                    {"message": "Player ID {player_id} was duplicated in field 'player-ids'"},
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
    cards_left = len(game.deck) - game.current_deck_index
    is_last_round = cards_left <= 15

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

    piles = []
    if not game.pile_one is None:
        piles.append(game.pile_one)
    if not game.pile_two is None:
        piles.append(game.pile_two)
    if not game.pile_three is None:
        piles.append(game.pile_three)
    if not game.pile_four is None:
        piles.append(game.pile_four)
    if not game.pile_five is None:
        piles.append(game.pile_five)

    response_body = {
        "current-state": game.status,
        "active-player-index": game.active_player_index,
        "use-advanced-scoring": game.use_advanced_scoring,
        "assign-wilds-on-take": game.assign_wilds_on_take,
        "piles": piles,
        "cards-left": cards_left,
        "last-round": is_last_round,
        "players": response_players
    }
    if game.removed_card:
        response_body["removed_card"] = game.removed_card
    return response_body
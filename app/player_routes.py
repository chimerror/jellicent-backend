from app import db
from app.models.player import Player, validate_player_id
from flask import Blueprint, jsonify, make_response, abort, request

players_bp = Blueprint("players", __name__, url_prefix = "/players")

@players_bp.route("", methods = ["GET"])
def get_all_players():
    players_response = []
    players = Player.query.all()
    for player in players:
        players_response.append({
            "id": player.id,
            "user-name": player.user_name,
            "display-name": player.display_name
        })
    return jsonify(players_response)

@players_bp.route("", methods = ["POST"])
def create_player():
    request_body = request.get_json()

    if not "user-name" in request_body:
        abort(make_response(
            { "message": "Missing required field 'user-name'" }, 400))

    new_user_name = request_body["user-name"]
    if not new_user_name.isalnum():
        abort(make_response(
            { "message": "Field 'user-name' must have one or more alphanumeric characters only" }
            , 400))

    existing_player = Player.query.filter_by(user_name = new_user_name).first()
    if not existing_player is None:
        abort(make_response(
            { "message": f"A player with user name '{new_user_name}' already exists" }
            , 409))

    if not "display-name" in request_body:
        abort(make_response(
            { "message": "Missing required field 'display-name'" }, 400))

    new_display_name = request_body["display-name"]
    if (not len(new_display_name) > 0) or new_display_name.isspace():
        abort(make_response(
            { "message": "Field 'display-name' must have one or more non-whitespace characters" }, 400))

    new_player = Player(
        user_name = request_body["user-name"],
        display_name = request_body["display-name"])
    db.session.add(new_player)
    db.session.commit()

    db.session.refresh(new_player, ["id"])
    return make_response(
        f"Player {new_player.user_name} with ID {new_player.id} successfully created",
        201)

@players_bp.route("/<player_id>", methods = ["GET"])
def get_player_by_id(player_id):
    player = validate_player_id(player_id)
    return {
        "id": player.id,
        "user-name": player.user_name,
        "display-name": player.display_name
    }

@players_bp.route("/<player_id>", methods = ["DELETE"])
def delete_player(player_id):
    player = validate_player_id(player_id)

    db.session.delete(player)
    db.session.commit()

    return make_response(f"Player {player.user_name} successfully deleted")

@players_bp.route("/<player_id>", methods = ["PUT"])
def update_player(player_id):
    player = validate_player_id(player_id)
    request_body = request.get_json()

    player.user_name = request_body["user-name"],
    player.display_name = request_body["display-name"]

    db.session.commit()

    return make_response(f"Player {player.user_name} successfully updated")
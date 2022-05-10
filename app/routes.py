from app import db
from app.models.player import Player
from flask import Blueprint, jsonify, make_response, abort, request

players_bp = Blueprint("players", __name__, url_prefix = "/players")

@players_bp.route("", methods = ["GET"])
def get_all_players():
    players_response = []
    players = Player.query.all()
    for player in players:
        players_response.append({
            "id": player.id,
            "user_name": player.user_name,
            "display_name": player.display_name
        })
    return jsonify(players_response)

@players_bp.route("", methods = ["POST"])
def create_player():
    request_body = request.get_json()
    new_player = Player(
        user_name = request_body["user_name"],
        display_name = request_body["display_name"])
    db.session.add(new_player)
    db.session.commit()

    return make_response(
        f"Player {new_player.user_name} successfully created",
        201)

@players_bp.route("/<player_id>", methods = ["GET"])
def get_player_by_id(player_id):
    player = validate_player_id(player_id)
    return {
        "id": player.id,
        "user_name": player.user_name,
        "display_name": player.display_name
    }

@players_bp.route("/<player_id>", methods = ["PUT"])
def update_player(player_id):
    player = validate_player_id(player_id)
    request_body = request.get_json()

    player.user_name = request_body["user_name"],
    player.display_name = request_body["display_name"]

    db.session.commit()

    return make_response(f"Player {player.user_name} successfully updated")

def validate_player_id(player_id):
    try:
        player_id = int(player_id)
    except:
        abort(make_response(
            {"message": f"{player_id} is not a valid player ID"}, 400))
    
    player = Player.query.get(player_id)

    if not player:
        abort(make_response(
            {"message": f"no player with ID {player_id} was found"}, 404))

    return player

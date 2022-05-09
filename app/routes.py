from flask import Blueprint, jsonify, make_response, abort

class Player:
    def __init__(self, id, user_name, display_name):
        self.id = id
        self.user_name = user_name
        self.display_name = display_name

players = [
    Player(1, "jayce", "Jayce Mitchell"),
    Player(2, "ada", "Ada Gates"),
    Player(2, "chimmy", "Chimerelda Error"),
]

players_bp = Blueprint("players", __name__, url_prefix = "/players")

@players_bp.route("", methods = ["GET"])
def get_all_players():
    players_response = []
    for player in players:
        players_response.append({
            "id": player.id,
            "user_name": player.user_name,
            "display_name": player.display_name
        })
    return jsonify(players_response)

@players_bp.route("/<player_id>", methods = ["GET"])
def get_player_by_id(player_id):
    player = validate_player_id(player_id)

    return {
        "id": player.id,
        "user_name": player.user_name,
        "display_name": player.display_name
    }

def validate_player_id(player_id):
    try:
        player_id = int(player_id)
    except:
        abort(make_response(
            {"message": f"{player_id} is not a valid player ID"}, 400))
    
    for player in players:
        if player.id == player_id:
            return player
    
    abort(make_response(
            {"message": f"player {player_id} is not a valid player ID"}, 404))

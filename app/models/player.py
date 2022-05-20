from app import db
from flask import make_response, abort

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_name = db.Column(db.String, nullable = False)
    display_name = db.Column(db.String, nullable = False)
    games = db.relationship("GamePlayer", back_populates = "player")

def validate_player_id(player_id, player_not_found_status_code = 404):
    try:
        player_id = int(player_id)
    except:
        abort(make_response(
            {"message": f"'{player_id}' is not a valid player ID"}, 400))
    
    player = Player.query.get(player_id)

    if not player:
        abort(make_response(
            {"message": f"No player with ID {player_id} was found"},
            player_not_found_status_code))

    return player
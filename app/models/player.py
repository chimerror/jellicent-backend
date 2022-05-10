from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_name = db.Column(db.String)
    display_name = db.Column(db.String)

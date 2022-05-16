from app import db

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_name = db.Column(db.String, nullable = False)
    display_name = db.Column(db.String, nullable = False)

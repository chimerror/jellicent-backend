import pytest
from app import create_app, db
from app.models.player import Player
from flask.signals import request_finished

@pytest.fixture
def app():
    app = create_app({"TESTING": True})

    @request_finished.connect_via(app)
    def expire_session(sender, response, **extra):
        db.session.remove()

    with app.app_context():
        db.create_all()
        yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def five_players(app):
    players = [
        Player(user_name = "jayce", display_name = "Jayce Mitchell"),
        Player(user_name = "chimmy", display_name = "Chimerelda Error"),
        Player(user_name = "ada", display_name = "Ada Gates"),
        Player(user_name = "glitch", display_name = "Glitch"),
        Player(user_name = "f0c5", display_name = "0xF0C5"),
    ]
    db.session.add_all(players)
    db.session.commit()
    return players
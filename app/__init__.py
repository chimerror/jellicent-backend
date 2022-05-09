from flask import Flask

def create_app(test_config = None):
    app = Flask(__name__)

    from .routes import players_bp
    app.register_blueprint(players_bp)

    return app
# app/__init__.py
from flask import Flask
from .routes import main as main_blueprint, data as data_blueprint, dashboard as dashboard_blueprint, db_manager as db_manager_blueprint, coach as coach_blueprint, arbiter as arbiter_blueprint, player as player_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(data_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(db_manager_blueprint)
    app.register_blueprint(coach_blueprint)
    app.register_blueprint(arbiter_blueprint)
    app.register_blueprint(player_blueprint)
    return app
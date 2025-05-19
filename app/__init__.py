# app/__init__.py
from flask import Flask
from .routes import main as main_blueprint, dashboard as dashboard_blueprint, db_manager as db_manager_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(db_manager_blueprint)
    return app
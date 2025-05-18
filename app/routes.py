# app/routes.py

from flask import Blueprint

main = Blueprint('main', __name__)

# homepage route
@main.route('/')
def home():
    return "Welcome to the homepage!"

# xxx route
@main.route('/xxx')
def xxx():
    return "This is the xxx page."
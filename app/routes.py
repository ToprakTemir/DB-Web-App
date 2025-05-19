# app/routes.py

from flask import Blueprint, render_template, redirect

main = Blueprint('main', __name__)
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# homepage route
@main.route('/')
def home():
    return redirect('/login')

@main.route('/login')
def login():
    return render_template('login.html')



@dashboard.route('/player')
def player_view():
    return render_template('player.html')


@dashboard.route('/coach')
def coach_view():
    return render_template('coach.html')

@dashboard.route('/db-manager')
def db_manager_view():
    return render_template('db-manager.html')

@dashboard.route('/arbiter')
def arbiter_view():
    return render_template('arbiter.html')
# app/routes.py

from flask import Blueprint, render_template, redirect, request, session
from .db import execute_sql_command

main = Blueprint('main', __name__)
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# homepage route
@main.route('/')
def home():
    return redirect('/login')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        results = execute_sql_command(f"CALL CheckUserCredentials('{request.form['username']}', '{request.form['password']}', @match_found, @user_table); SELECT @match_found, @user_table;")
        query_result = results[0]
        found, table = query_result[0]
        if found:
            if table == 'DBManagers':
                session['roles'] = ['db-manager']
                return redirect('/dashboard/db-manager')
            elif table == 'Players':
                session['roles'] = ['player']
                return redirect('/dashboard/player')
            elif table == 'Coaches':
                session['roles'] = ['coach']
                return redirect('/dashboard/coach')
            elif table == 'Arbiters':
                session['roles'] = ['arbiter']
                return redirect('/dashboard/arbiter')
    
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('roles', None)
    return redirect('/login')



@dashboard.route('/player')
def player_view():
    try:
        if session['roles'] == ['player']:
            return render_template('player.html')
        
        return redirect(f'/dashboard/{session['roles'][0]}')
    
    except:
        pass
    return redirect('/login')
    
@dashboard.route('/coach')
def coach_view():
    try:
        if session['roles'] == ['coach']:
            return render_template('coach.html')
        
        return redirect(f'/dashboard/{session['roles'][0]}')

    except:
        pass
    return redirect('/login')

@dashboard.route('/db-manager')
def db_manager_view():
    try:
        if session['roles'] == ['db-manager']:
            return render_template('db-manager.html')
        
        return redirect(f'/dashboard/{session['roles'][0]}')

    except:
        pass
    return redirect('/login')

@dashboard.route('/arbiter')
def arbiter_view():
    try:
        if session['roles'] == ['arbiter']:
            return render_template('arbiter.html')
        
        return redirect(f'/dashboard/{session['roles'][0]}')

    except:
        pass
    return redirect('/login')
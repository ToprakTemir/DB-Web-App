# app/routes.py

from flask import Blueprint, render_template, redirect, request, session, jsonify
from .db import execute_sql_command

main = Blueprint('main', __name__)
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')
db_manager = Blueprint('db_manager', __name__, url_prefix='/dashboard/db-manager')


# ----- MAIN ROUTES (Prefix: None) -----

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


# ----- DASHBOARD ROUTES (Prefix: /dashboard) -----

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


# ----- DB MANAGER ROUTES (Prefix: /dashboard/db-manager) -----

@db_manager.route('/add-user', methods=['POST'])
def add_user():
    
    user_type = request.form['user_type']
    
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    surname = request.form['surname']
    nationality = request.form['nationality']

    if user_type == 'player':
        date_of_birth = request.form['date_of_birth']
        fide_id = request.form['fide_id']
        elo_rating = request.form['elo_rating']
        title_id = request.form['title_id']

        team_id = request.form['team_id'] # Optional
        

        results = execute_sql_command(f"CALL InsertPlayer('{username}', '{password}', '{name}', '{surname}', '{nationality}', '{date_of_birth}', {fide_id}, {elo_rating}, {title_id});")

        # If optional team ID is provided and player insertion didn't fail, insert to PlayerTeams
        if team_id != '' and not isinstance(results, str):
            results = execute_sql_command(f"CALL InsertPlayerTeam('{username}', {team_id});")
            # If PlayerTeams insertion fails, revert player insertion
            if isinstance(results, str):
                execute_sql_command(f"DELETE FROM TABLE Players WHERE username = {username}")

    elif user_type == 'coach':
        team_id = request.form['team_id']
        start_date = request.form['contract_start']
        end_date = request.form['contract_end']

        coach_certification = request.form['coach_certification'] # Optional

        results = execute_sql_command(f"CALL InsertCoach('{username}', '{password}', '{name}', '{surname}', '{nationality}', {team_id}, '{start_date}', '{end_date}');")

        if coach_certification != '' and not isinstance(results, str):
            results = execute_sql_command(f"CALL InsertCoachCertification('{username}', '{coach_certification}');")
            if isinstance(results, str):
                execute_sql_command(f"DELETE FROM TABLE Coaches WHERE username = {username}")

    elif user_type == 'arbiter':
        experience_level = request.form['experience_level']

        arbiter_certification = request.form['arbiter_certification'] # Optional

        results = execute_sql_command(f"CALL InsertArbiter('{username}', '{password}', '{name}', '{surname}', '{nationality}', '{experience_level}');")

        if arbiter_certification != '' and not isinstance(results, str):
            results = execute_sql_command(f"CALL InsertArbiterCertification('{username}', '{arbiter_certification}');")
            if isinstance(results, str):
                execute_sql_command(f"DELETE FROM TABLE Arbiters WHERE username = {username}")

    return redirect('/dashboard/db-manager')

@db_manager.route('/fetch-halls')
def fetch_halls():
    results = execute_sql_command("SELECT * FROM Halls;")
    rows = results[0]
    columns = ['hall_id', 'hall_name', 'country', 'capacity']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@db_manager.route('/rename-hall', methods=['POST'])
def rename_hall():
    hall_id = request.form['hall_id']
    new_name = request.form['new_hall_name']
    results = execute_sql_command(f"UPDATE Halls SET hall_name = '{new_name}' WHERE hall_id = '{hall_id}';")
    return redirect('/dashboard/db-manager')
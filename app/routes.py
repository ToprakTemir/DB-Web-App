# app/routes.py

from flask import Blueprint, render_template, redirect, request, session, jsonify
from .db import execute_sql_command

main = Blueprint('main', __name__)
data = Blueprint('data', __name__, url_prefix='/data')
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')
db_manager = Blueprint('db_manager', __name__, url_prefix='/dashboard/db-manager')
coach = Blueprint('coach', __name__, url_prefix='/dashboard/coach')


# ----- MAIN ROUTES (Prefix: None) -----

@main.route('/')
def home():
    return redirect('/login')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        results = execute_sql_command(f"CALL CheckUserCredentials('{username}', '{password}', @match_found, @user_table); SELECT @match_found, @user_table;")
        query_result = results[1]
        found, table = query_result[0]
        if found:
            session['username'] = username
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





# ----- DATA ROUTES (Prefix: /data) -----

@data.route('/halls')
def fetch_halls():
    results = execute_sql_command("SELECT * FROM Halls;")
    rows = results[0]
    columns = ['hall_id', 'hall_name', 'country', 'capacity']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@data.route('/available-arbiters')
def fetch_available_arbiters():
    date = request.args.get('date')
    time_slot = request.args.get('time_slot')

    results = execute_sql_command(f"SELECT name, surname FROM Arbiters WHERE username NOT IN (SELECT arbiter_username FROM Matches WHERE date = (STR_TO_DATE({date}, '%d-%m-%Y')) AND time_slot = {time_slot});")
    rows = results[0]
    columns = ['name', 'surname']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@data.route('/opponent-teams')
def fetch_opponent_teams():
    results = execute_sql_command(f"SELECT * FROM Teams WHERE team_id != (SELECT team_id FROM Coaches WHERE username = '{session['username']}');")
    rows = results[0]
    columns = ['team_id', 'team_name', 'sponsor_id']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@data.route('/tables')
def tables():
    hall_id = request.args.get('hall_id')

    results = execute_sql_command(f"SELECT table_id FROM Tables WHERE hall_id = {hall_id};")
    rows = results[0]
    columns = ['table_id']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)





# ----- DASHBOARD ROUTES (Prefix: /dashboard) -----

@dashboard.route('/player')
def player_dashboard():
    try:
        if session['roles'] == ['player']:
            return render_template('player.html')
        
        return redirect(f'/dashboard/{session['roles'][0]}')
    
    except:
        pass
    return redirect('/login')
    
@dashboard.route('/coach')
def coach_dashboard():
    try:
        if session['roles'] == ['coach']:
            return render_template('coach.html')
        
        return redirect(f'/dashboard/{session['roles'][0]}')

    except:
        pass
    return redirect('/login')

@dashboard.route('/db-manager')
def db_manager_dashboard():
    try:
        if session['roles'] == ['db-manager']:
            return render_template('db-manager.html')
        
        return redirect(f'/dashboard/{session['roles'][0]}')

    except:
        pass
    return redirect('/login')

@dashboard.route('/arbiter')
def arbiter_dashboard():
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

@db_manager.route('/rename-hall', methods=['POST'])
def rename_hall():
    hall_id = request.form['hall_id']
    new_name = request.form['new_hall_name']
    results = execute_sql_command(f"UPDATE Halls SET hall_name = '{new_name}' WHERE hall_id = '{hall_id}';")
    return redirect('/dashboard/db-manager')





# ----- COACH ROUTES (Prefix: /dashboard/coach) -----

@coach.route('/create-match', methods=['POST'])
def create_match():
    prev_id = execute_sql_command(f"SELECT MAX(match_id) FROM matches;")[0][0][0]
    if isinstance(prev_id, int):
        match_id = prev_id + 1
    else: 
        match_id = 1
    date = request.form['match_date']
    time_slot = request.form['time_slot']
    hall_id = request.form['hall_id']
    table_id = request.form['table_id']
    team1_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{session['username']}';")[0][0][0]
    team2_id = request.form['opponent_team_id']
    arbiter_username = request.form['arbiter_name']
    rating = 'NULL'

    results = execute_sql_command(f"CALL InsertMatch({match_id}, '{date}', '{time_slot}', {hall_id}, {table_id}, {team1_id}, {team2_id}, '{arbiter_username}', {rating});")
    return redirect('/dashboard/coach')

# app/routes.py

from flask import Blueprint, render_template, redirect, request, session, jsonify
from .db import execute_sql_command
import json

main = Blueprint('main', __name__)
data = Blueprint('data', __name__, url_prefix='/data')
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')
db_manager = Blueprint('db_manager', __name__, url_prefix='/dashboard/db-manager')
coach = Blueprint('coach', __name__, url_prefix='/dashboard/coach')
arbiter = Blueprint('arbiter', __name__, url_prefix='/dashboard/arbiter')





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

    results = execute_sql_command(f"SELECT username, name, surname FROM Arbiters WHERE username NOT IN (SELECT arbiter_username FROM Matches WHERE date = (STR_TO_DATE({date}, '%d-%m-%Y')) AND time_slot = {time_slot});")
    rows = results[0]
    columns = ['username', 'name', 'surname']

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
def fetch_tables():
    hall_id = request.args.get('hall_id')

    results = execute_sql_command(f"SELECT table_id FROM Tables WHERE hall_id = {hall_id};")
    rows = results[0]
    columns = ['table_id']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@data.route('/unassigned-matches')
def fetch_unassigned_matches():
    response = fetch_coach_matches()
    matches = json.loads(response.get_data(as_text=True))

    # Filter matches with either side unassigned
    unassigned_matches = [match for match in matches if not match['player_name']]

    return jsonify(unassigned_matches)

@data.route('/coach-matches')
def fetch_coach_matches():
    coach_username = session['username']
    team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}';")[0][0][0]
    
    # Query to get all matches for the coach's team with player information
    sql_query = f"""
    SELECT m.match_id, DATE_FORMAT(m.date, '%d-%m-%Y') as match_date, m.time_slot, 
       h.hall_name, m.table_id, opp_t.team_name as opponent_team_name,
       CONCAT(a.name, ' ', a.surname) as arbiter_name,
       CONCAT(yp.name, ' ', yp.surname) as player_name,
       CONCAT(opp.name, ' ', opp.surname) as opponent_player_name,
       m.ratings
    FROM Matches m
    JOIN Halls h ON m.hall_id = h.hall_id
    JOIN Teams opp_t ON m.team2_id = opp_t.team_id
    JOIN Arbiters a ON m.arbiter_username = a.username
    LEFT JOIN MatchAssignments ma ON ma.match_id = m.match_id
    LEFT JOIN Players yp ON yp.username = ma.white_player
    LEFT JOIN Players opp ON opp.username = ma.black_player
    WHERE m.team1_id = {team_id}

    UNION

    SELECT m.match_id, DATE_FORMAT(m.date, '%d-%m-%Y') as match_date, m.time_slot, 
       h.hall_name, m.table_id, opp_t.team_name as opponent_team_name,
       CONCAT(a.name, ' ', a.surname) as arbiter_name,
       CONCAT(yp.name, ' ', yp.surname) as player_name,
       CONCAT(opp.name, ' ', opp.surname) as opponent_player_name,
       m.ratings
    FROM Matches m
    JOIN Halls h ON m.hall_id = h.hall_id
    JOIN Teams opp_t ON m.team1_id = opp_t.team_id
    JOIN Arbiters a ON m.arbiter_username = a.username
    LEFT JOIN MatchAssignments ma ON ma.match_id = m.match_id
    LEFT JOIN Players yp ON yp.username = ma.black_player
    LEFT JOIN Players opp ON opp.username = ma.white_player
    WHERE m.team2_id = {team_id}

    """
    
    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['match_id', 'match_date', 'time_slot', 'hall_name', 'table_id', 'opponent_team_name', 
               'arbiter_name', 'player_name', 'opponent_player_name', 'rating']
    
    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]
    
    return jsonify(result)

@data.route('/available-players')
def fetch_available_players():
    match_id = request.args.get('match_id')
    coach_username = session['username']
    team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}';")[0][0][0]
    
    # Get match date and time
    match_info = execute_sql_command(f"SELECT date, time_slot FROM Matches WHERE match_id = {match_id};")
    match_date = match_info[0][0][0]
    match_time_slot = match_info[0][0][1]
    
    # Query to get players from coach's team who are not already assigned to other matches at same time
    sql_query = f"""
    SELECT p.username as player_username, p.name, p.surname, p.elo_rating as rating
    FROM Players p
    JOIN PlayerTeams pt ON p.username = pt.username
    WHERE pt.team_id = {team_id}
    AND NOT EXISTS (
    SELECT 1
    FROM MatchAssignments ma
    JOIN Matches m ON ma.match_id = m.match_id
    WHERE m.date = '{match_date}' 
    AND m.time_slot = {match_time_slot}
    AND (ma.white_player = p.username OR ma.black_player = p.username)
    )
    ORDER BY p.elo_rating DESC;
    """
    
    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['player_username', 'name', 'surname', 'rating']
    
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
        
        try:
            execute_sql_command(f"CALL InsertPlayer('{username}', '{password}', '{name}', '{surname}', '{nationality}', '{date_of_birth}', '{fide_id}', {elo_rating}, {title_id});")
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        try:
            if team_id:
                execute_sql_command(f"CALL InsertPlayerTeam('{username}', {team_id});")
        # If PlayerTeams insertion fails, revert Players insertion
        except Exception as e:
            execute_sql_command(f"DELETE FROM TABLE Players WHERE username = '{username}';")
            return jsonify({"success": False, "message": str(e)})
        

    elif user_type == 'coach':
        team_id = request.form['team_id']
        start_date = request.form['contract_start']
        end_date = request.form['contract_end']

        coach_certification = request.form['coach_certification'] # Optional

        try:
            execute_sql_command(f"CALL InsertCoach('{username}', '{password}', '{name}', '{surname}', '{nationality}', {team_id}, '{start_date}', '{end_date}');")
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        try:
            execute_sql_command(f"CALL InsertCoachCertification('{username}', '{coach_certification}');")
        except Exception as e:
            execute_sql_command(f"DELETE FROM TABLE Coaches WHERE username = {username}")
            return jsonify({"success": False, "message": str(e)})

    elif user_type == 'arbiter':
        experience_level = request.form['experience_level']

        arbiter_certification = request.form['arbiter_certification'] # Optional

        try:
            execute_sql_command(f"CALL InsertArbiter('{username}', '{password}', '{name}', '{surname}', '{nationality}', '{experience_level}');")
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
        try:
            execute_sql_command(f"CALL InsertArbiterCertification('{username}', '{arbiter_certification}');")
        except Exception as e:
            execute_sql_command(f"DELETE FROM TABLE Arbiters WHERE username = {username}")
            return jsonify({"success": False, "message": str(e)})

    return redirect('/dashboard/db-manager')

@db_manager.route('/rename-hall', methods=['POST'])
def rename_hall():
    hall_id = request.form['hall_id']
    new_name = request.form['new_hall_name']
    try:
        execute_sql_command(f"UPDATE Halls SET hall_name = '{new_name}' WHERE hall_id = '{hall_id}';")
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    return jsonify({"success": True})





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
    ratings = 'NULL'

    try:
        execute_sql_command(f"CALL InsertMatch({match_id}, '{date}', '{time_slot}', {hall_id}, {table_id}, {team1_id}, {team2_id}, '{arbiter_username}', {ratings});")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@coach.route('/assign-player', methods=['POST'])
def assign_player():
    data = request.json
    match_id = data.get('match_id')
    player_username = data.get('player_username')
    coach_username = session['username']

    team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}';")[0][0][0]

    # Get both teams from the match
    match_check = execute_sql_command(f"SELECT team1_id, team2_id FROM Matches WHERE match_id = {match_id};")
    if not match_check or not match_check[0]:
        return jsonify({"success": False, "message": "Match not found."})

    team1_id = match_check[0][0][0]
    team2_id = match_check[0][0][1]

    if team_id != team1_id and team_id != team2_id:
        return jsonify({"success": False, "message": "This match does not belong to your team."})

    # Determine player side
    is_white = team_id == team1_id
    player_column = "white_player" if is_white else "black_player"
    player_column_team = "team1_id" if is_white else "team2_id"
    opponent_column = "black_player" if is_white else "white_player"
    opponent_column_team = "team2_id" if is_white else "team1_id"

    assignment_check = execute_sql_command(f"SELECT COUNT(*) FROM MatchAssignments WHERE match_id = {match_id};")

    if assignment_check[0][0][0] > 0:
        try:
            execute_sql_command(f"UPDATE MatchAssignments SET {player_column} = '{player_username}' WHERE match_id = {match_id};")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    else:
        try:
            execute_sql_command(f"INSERT INTO MatchAssignments(match_id, {player_column}, {opponent_column}, result, {player_column_team}, {opponent_column_team}) VALUES ({match_id}, '{player_username}', NULL, NULL, {team_id}, NULL);")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})

    

@coach.route('/delete-match/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    coach_username = session['username']
    team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}';")[0][0][0]
    
    # Check if match belongs to coach's team
    check_query = f"SELECT COUNT(*) FROM Matches WHERE match_id = {match_id} AND team1_id = {team_id};"
    is_coach_match = execute_sql_command(check_query)[0][0][0] > 0
    
    if not is_coach_match:
        return jsonify({"success": False, "message": "You don't have permission to delete this match."})
    
    try:
        # Delete associated records from MatchAssignments first (due to foreign key constraints)
        execute_sql_command(f"DELETE FROM MatchAssignments WHERE match_id = {match_id};")
        
        # Then delete the match itself
        execute_sql_command(f"DELETE FROM Matches WHERE match_id = {match_id};")
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})





# ----- ARBITER ROUTES (Prefix: /dashboard/arbiter) -----



@arbiter.route('/assigned-matches')
def fetch_assigned_matches():
    arbiter_username = session['username']

    sql_query = f'''
    SELECT m.match_id, DATE_FORMAT(m.date, '%d-%m-%Y') as match_date, m.time_slot, 
       h.hall_name, m.table_id, t1.team_name as team1, t2.team_name as team2,
       CONCAT(p1.name, ' ', p1.surname) as player1,
       CONCAT(p2.name, ' ', p2.surname) as player2,
       m.ratings
    FROM Matches m
    JOIN Halls h ON m.hall_id = h.hall_id
    JOIN Teams t1 ON m.team1_id = t1.team_id
    JOIN Teams t2 ON m.team2_id = t2.team_id
    JOIN MatchAssignments ma ON ma.match_id = m.match_id
    JOIN Players p1 ON p1.username = ma.white_player
    JOIN Players p2 ON p2.username = ma.black_player
    WHERE m.arbiter_username = '{arbiter_username}'
    
    '''

    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['match_id', 'match_date', 'time_slot', 'hall_name', 'table_id', 'team1', 'team2', 'player1', 'player2', 'ratings']
    
    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]
    
    return jsonify(result)
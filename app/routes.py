# app/routes.py

from flask import Blueprint, render_template, redirect, request, session, jsonify
from app.common import execute_sql_command, encrypt_password, verify_password, password_policy
import json

main = Blueprint('main', __name__)
data = Blueprint('data', __name__, url_prefix='/data')
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')
db_manager = Blueprint('db_manager', __name__, url_prefix='/db-manager')
coach = Blueprint('coach', __name__, url_prefix='/coach')
arbiter = Blueprint('arbiter', __name__, url_prefix='/arbiter')
player = Blueprint('player', __name__, url_prefix='/player')


# ----- MAIN ROUTES (Prefix: None) -----

@main.route('/')
def home():
    return redirect('/login')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        plain_password = request.form['password']

        password_tuple_list = execute_sql_command(f"CALL CheckUserCredentials('{username}');")[0]
        
        if password_tuple_list:
            hashed_password, role = password_tuple_list[0]
            if verify_password(plain_password, hashed_password):
                session['username'] = username
                session['roles'] = [role]
                return jsonify({'success': True, 'redirect': '/dashboard'})
        return jsonify({"success": False, "message": "Incorrect username or password."})
    
    else:
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

    sql_query = f'''
    SELECT username, name, surname
    FROM Arbiters
    WHERE username NOT IN 
    (SELECT arbiter_username FROM Matches WHERE date = (STR_TO_DATE('{date}', '%d-%m-%Y')) AND (time_slot = '{time_slot}' OR time_slot = '{int(time_slot) + 1}' OR time_slot = '{int(time_slot) - 1}'))
    '''


    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['username', 'name', 'surname']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@data.route('/opponent-teams')
def fetch_opponent_teams():
    results = execute_sql_command(f"SELECT * FROM Teams WHERE team_id NOT IN (SELECT team_id FROM Coaches WHERE username = '{session['username']}' AND contract_start < CURDATE() AND contract_finish > CURDATE());")
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
    try:
        team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}' AND contract_start < CURDATE() AND contract_finish > CURDATE();")[0][0][0]
    except:
        return jsonify([])
    
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

    try:
        results = execute_sql_command(sql_query)
        rows = results[0]
    except Exception as error:
        print(f"Error executing SQL query: {error}")
        return jsonify({"error": "Failed to fetch matches."}), 500

    columns = ['match_id', 'match_date', 'time_slot', 'hall_name', 'table_id', 'opponent_team_name', 
               'arbiter_name', 'player_name', 'opponent_player_name', 'rating']
    
    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]
    
    return jsonify(result)

@data.route('/available-players')
def fetch_available_players():
    match_id = request.args.get('match_id')
    coach_username = session['username']
    try:
        team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}' AND contract_start < CURDATE() AND contract_finish > CURDATE();")[0][0][0]
    except:
        return jsonify([])

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
    AND (m.time_slot = '{match_time_slot}' OR m.time_slot = '{int(match_time_slot) + 1}' OR m.time_slot = '{int(match_time_slot) - 1}')
    AND (ma.white_player = p.username OR ma.black_player = p.username)
    )
    ORDER BY p.elo_rating DESC;
    """

    print(sql_query)
    
    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['player_username', 'name', 'surname', 'ratings']
    
    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]
    
    return jsonify(result)

@data.route('/coach-team')
def fetch_coach_team():
    coach_username = session['username']
    sql_query = f"SELECT t.team_name FROM Teams t JOIN Coaches c ON c.team_id = t.team_id WHERE username = '{coach_username}' AND contract_start < CURDATE() AND contract_finish > CURDATE()"
    try:
        team_name = execute_sql_command(sql_query)[0][0][0]
    except:
        return jsonify([])

    return jsonify({'team_name': team_name})





# ----- DASHBOARD ROUTES (Prefix: /dashboard) -----

@dashboard.route('/')
def show_dashboard():
    role = session.get('roles', [None])[0]
    if role in ['db-manager', 'coach', 'player', 'arbiter', 'player', 'arbiter']:
        return render_template(f"{role}.html")
    return redirect('login')


# ----- DB MANAGER ROUTES (Prefix: /db-manager) -----

@db_manager.route('/add-user', methods=['POST'])
def add_user():
    
    user_type = request.form['user_type']
    
    username = request.form['username']
    password = request.form['password']
    
    policy_check, message = password_policy(password)
    if not policy_check:
        return jsonify({"success": False, "message": message})
   
    password = encrypt_password(password)
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
            execute_sql_command(f"DELETE FROM Players WHERE username = '{username}';")
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
            execute_sql_command(f"DELETE FROM Coaches WHERE username = {username}")
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
            execute_sql_command(f"DELETE FROM Arbiters WHERE username = {username}")
            return jsonify({"success": False, "message": str(e)})

    return jsonify({"success": True})

@db_manager.route('/rename-hall', methods=['POST'])
def rename_hall():
    hall_id = request.form['hall_id']
    new_name = request.form['new_hall_name']
    try:
        execute_sql_command(f"UPDATE Halls SET hall_name = '{new_name}' WHERE hall_id = '{hall_id}';")
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    return jsonify({"success": True})

@db_manager.route('/delete-user/<username>', methods=['DELETE'])
def delete_user(username):
    sql_query = f'''
    SELECT username, 'players' AS role
    FROM Players
    WHERE username = '{username}'
    
    UNION

    SELECT username, 'coaches' AS role
    FROM Coaches
    WHERE username = '{username}'
    
    UNION
    
    SELECT username, 'arbiters' AS role
    FROM Arbiters
    WHERE username = '{username}';
    '''

    try:
        _, table = execute_sql_command(sql_query)[0][0]
        sql_query = f'''
        DELETE FROM {table} WHERE username = '{username}';
        '''
        execute_sql_command(sql_query)
        return jsonify({"success": True})
    except:
        return jsonify({"success": False, "message": "A player, coach or arbiter with this username does not exist."})



# ----- COACH ROUTES (Prefix: /coach) -----

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
    try:
        team1_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{session['username']}' AND contract_start < CURDATE() AND contract_finish > CURDATE();")[0][0][0]
    except:
        return jsonify({"success": False, "message": "Failed to create fatch: You don't have an active contract."})
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


    try:
        player_team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}' AND contract_start < CURDATE() AND contract_finish > CURDATE();")[0][0][0]
    except:
        return jsonify({"success": False, "message": "Failed to assign player: You don't have an active contract."})

    # Get both teams from the match
    match_check = execute_sql_command(f"SELECT team1_id, team2_id FROM Matches WHERE match_id = {match_id};")
    if not match_check or not match_check[0]:
        return jsonify({"success": False, "message": "Match not found."})

    team1_id = match_check[0][0][0]
    team2_id = match_check[0][0][1]

    if player_team_id != team1_id and player_team_id != team2_id:
        return jsonify({"success": False, "message": "This match does not belong to your team."})

    # Determine player side
    is_white = player_team_id == team1_id
    player_column = "white_player" if is_white else "black_player"
    player_column_team = "team1_id" if is_white else "team2_id"
    opponent_column = "black_player" if is_white else "white_player"
    opponent_column_team = "team2_id" if is_white else "team1_id"
    opponent_team_id = team2_id if is_white else team1_id

    assignment_check = execute_sql_command(f"SELECT COUNT(*) FROM MatchAssignments WHERE match_id = {match_id};")

    if assignment_check[0][0][0] > 0:
        try:
            execute_sql_command(f"UPDATE MatchAssignments SET {player_column} = '{player_username}' WHERE match_id = {match_id};")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    else:
        try:
            execute_sql_command(f"INSERT INTO MatchAssignments(match_id, {player_column}, {opponent_column}, result, {player_column_team}, {opponent_column_team}) VALUES ({match_id}, '{player_username}', NULL, NULL, {player_team_id}, {opponent_team_id});")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})

    

@coach.route('/delete-match/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    coach_username = session['username']
    try:
        team_id = execute_sql_command(f"SELECT team_id FROM Coaches WHERE username = '{coach_username}' AND contract_start < CURDATE() AND contract_finish > CURDATE();")[0][0][0]
    except:
        return jsonify({"success": False, "message": "Failed to delete match: You don't have an active contract."})

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



# ----- ARBITER ROUTES (Prefix: /arbiter) -----

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

@arbiter.route('/rating-stats')
def fetch_rating_stats():
    arbiter_username = session['username']

    sql_query = f'''
    SELECT COUNT(*) AS total_matches_rated, ROUND(AVG(ratings), 1) AS average_rating_given
    FROM Matches
    WHERE arbiter_username = '{arbiter_username}' AND ratings IS NOT NULL
    
    '''

    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['total_matches_rated', 'average_rating_given']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@arbiter.route('/rate-match', methods=['POST'])
def rate_match():
    data = request.json
    match_id = data.get('match_id')
    rating = data.get('rating')

    sql_query = f'''
    UPDATE Matches
    SET ratings = {rating}
    WHERE match_id = {match_id}
    
    '''

    try:
        execute_sql_command(sql_query)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})



# ----- PLAYER ROUTES (Prefix: /player) -----

@player.route('/profile')
def fetch_profile():
    player_username = session['username']

    sql_query = f'''
    SELECT CONCAT(p.name, ' ', p.surname) as fullname,
    p.fide_id, p.nationality, p.elo_rating, t.title_name
    FROM Players p
    JOIN Titles t ON p.title_id = t.title_id
    WHERE p.username = '{player_username}'

    '''

    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['fullname', 'fide_id', 'nationality', 'elo_rating', 'title_name']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]


    sql_query = f'''
    SELECT t.team_name
    FROM Teams t
    JOIN PlayerTeams pt ON t.team_id = pt.team_id
    JOIN Players p ON p.username = pt.username
    WHERE p.username = '{player_username}'

    '''

    results = execute_sql_command(sql_query)
    rows = results[0]
    result[0]['teams'] = [row[0] for row in rows]

    return jsonify(result)

@player.route('/opponent-history')
def fetch_opponent_history():
    player_username = session['username']

    sql_query = f'''
    SELECT CONCAT(p.name, ' ', p.surname) as player_name,
    p.elo_rating, ti.title_name, p.nationality, COUNT(*) as times_played
    FROM MatchAssignments ma
    JOIN Players p ON ma.black_player = p.username
    JOIN Titles ti ON ti.title_id = p.title_id
    JOIN Matches m ON m.match_id = ma.match_id
    WHERE ma.white_player = '{player_username}' AND m.date < CURDATE()
    GROUP BY ma.black_player

    UNION

    SELECT CONCAT(p.name, ' ', p.surname) as player_name,
    p.elo_rating, ti.title_name, p.nationality, COUNT(*) as times_played
    FROM MatchAssignments ma
    JOIN Players p ON ma.white_player = p.username
    JOIN Titles ti ON ti.title_id = p.title_id
    JOIN Matches m ON m.match_id = ma.match_id
    WHERE ma.black_player = '{player_username}' AND m.date < CURDATE()
    GROUP BY ma.white_player

    ORDER BY times_played DESC
    '''

    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['player_name', 'elo_rating', 'title_name', 'nationality', 'times_played']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)

@player.route('/frequent-opponent')
def fetch_frequent_opponent():
    opponent_history = fetch_opponent_history()

    opponent_list = json.loads(opponent_history.get_data(as_text=True))
    if len(opponent_list) == 0:
        return jsonify({'player_name': '-', 'elo_rating': '-', 'title_name': '', 'nationality': '', 'times_played': '-'})
    else:
        tie_count = 1
        top_opponent = opponent_list[0]
        most_matches = top_opponent['times_played']
        total_elo = top_opponent['elo_rating']
        names = top_opponent['player_name']
        for opponent in opponent_list[1:]:
            if opponent['times_played'] < most_matches:
                break
            tie_count += 1
            total_elo += opponent['elo_rating']
            names += f", {opponent['player_name']}"
        avg_elo = total_elo / tie_count
        return jsonify({'player_name': names, 'elo_rating': avg_elo, 'title_name': '', 'nationality': '', 'times_played': top_opponent['times_played']})


@player.route('/match-history')
def fetch_match_history():
    player_username = session['username']

    sql_query = f'''
    SELECT DATE_FORMAT(m.date, '%d-%m-%Y') as date, m.time_slot, h.hall_name, m.table_id, yt.team_name, opp_t.team_name,
    CONCAT(opp.name, ' ', opp.surname) as opponent_name,
    CONCAT(a.name, ' ', a.surname) as arbiter_name,
    m.ratings, ma.result
    FROM Matches m
    JOIN MatchAssignments ma ON m.match_id = ma.match_id
    JOIN Teams yt ON yt.team_id = ma.team1_id
    JOIN Teams opp_t ON opp_t.team_id = ma.team2_id
    JOIN Halls h ON m.hall_id = h.hall_id
    JOIN Arbiters a ON m.arbiter_username = a.username
    JOIN Players opp ON opp.username = ma.black_player
    WHERE ma.white_player = '{player_username}' AND m.date < CURDATE()

    UNION

    SELECT DATE_FORMAT(m.date, '%d-%m-%Y') as date, m.time_slot, h.hall_name, m.table_id, yt.team_name, opp_t.team_name,
    CONCAT(opp.name, ' ', opp.surname) as opponent_name,
    CONCAT(a.name, ' ', a.surname) as arbiter_name,
    m.ratings, ma.result
    FROM Matches m
    JOIN MatchAssignments ma ON m.match_id = ma.match_id
    JOIN Teams yt ON yt.team_id = ma.team2_id
    JOIN Teams opp_t ON opp_t.team_id = ma.team1_id
    JOIN Halls h ON m.hall_id = h.hall_id
    JOIN Arbiters a ON m.arbiter_username = a.username
    JOIN Players opp ON opp.username = ma.white_player
    WHERE ma.black_player = '{player_username}' AND m.date < CURDATE()

    ORDER BY date DESC

    '''

    results = execute_sql_command(sql_query)
    rows = results[0]
    columns = ['date', 'slot', 'hall_name', 'table', 'your_team', 'opponent_team', 'opponent_name', 'arbiter_name', 'rating', 'result']

    # Convert to list of dicts
    result = [dict(zip(columns, row)) for row in rows]

    return jsonify(result)
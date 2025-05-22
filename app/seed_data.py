import math
import pandas as pd
import os

import mysql.connector
from app.common import get_db_connection, execute_sql_file, encrypt_password

def seed_data():

    # Read Excel file, sheet_name=None returns a dictionary of DataFrames with sheet names as keys
    base_dir = os.path.dirname(__file__)  # Directory of the current script
    data_file = pd.read_excel(f'{base_dir}/ChessDB_initial_data.xlsx', sheet_name=None, engine='openpyxl')

    # Connect to DB
    conn = get_db_connection()
    cursor = conn.cursor()

    # first drop all tables
    for table_name in data_file.keys():
        print(f"dropping table {table_name}")
        # Temporarily disable foreign key checks to avoid constraint violations
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        drop_query = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(drop_query)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # recreate the tables
    execute_sql_file(f'{base_dir}/sql/schema.sql')

    print("--------------------------------------------------------------")

    insertion_order = [
        "DBManagers",
        "Titles",
        "Players",
        "Sponsors",
        "Teams",
        "Coaches",
        "CoachCertifications",
        "Arbiters",
        "ArbiterCertifications",
        "Halls",
        "Tables",
        "Matches",
        "PlayerTeams",
        "MatchAssignments"
    ]

    for table_name in insertion_order:
        if table_name not in data_file.keys():
            print(f"table not found in data file: {table_name}")
            continue

        data = data_file[table_name]
        columns = data.columns.tolist()

        # this block assumes PlayerTeams table is already filled!
        if table_name == 'MatchAssignments':
            white_players = data['white_player'].tolist()
            black_players = data['black_player'].tolist()
            white_teams_query = f"SELECT team_id FROM PlayerTeams WHERE username IN ({', '.join(map(repr, white_players))})"
            black_teams_query = f"SELECT team_id FROM PlayerTeams WHERE username IN ({', '.join(map(repr, black_players))})"
            cursor.execute(white_teams_query)
            white_teams = cursor.fetchall()
            cursor.execute(black_teams_query)
            black_teams = cursor.fetchall()
            data['team1_id'] = [team[0] for team in white_teams]
            data['team2_id'] = [team[0] for team in black_teams]
            columns += ['team1_id', 'team2_id']

        column_names = ', '.join(columns) # column names seperated by ', '
        column_value_placeholders = ', '.join(['%s'] * len(columns)) # %s for each column

        insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({column_value_placeholders})"
        print(insert_query)

        for idx, row in data.iterrows():

            # Special fixes
            row_data = []
            for col, val in zip(columns, row):
                # convert NaN -> None
                if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
                    val = None

                # converting dates from DD-MM-YYYY to YYYY-MM-DD
                if isinstance(val, str) and '-' in val and col in ['date_of_birth', 'contract_start', 'contract_finish']:
                    # Convert from DD-MM-YYYY to YYYY-MM-DD
                    try:
                        day, month, year = val.split('-')
                        val = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    except Exception as e:
                        print(f"Failed to convert date '{val}' in column '{col}': {e}")
                if isinstance(val, str) and col == 'password':
                    val = encrypt_password(val)
                row_data.append(val)


            row_data = tuple(row_data)
            try:
                cursor.execute(insert_query, row_data)
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                print(f"Missed row data: {row_data}")
                continue


    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed_data()
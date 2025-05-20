import math

import pandas as pd
import mysql.connector
from app.db import get_db_connection, execute_sql_file

# Read Excel file, sheet_name=None returns a dictionary of DataFrames with sheet names as keys
data_file = pd.read_excel('ChessDB_initial_data.xlsx', sheet_name=None, engine='openpyxl')

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
execute_sql_file('sql/schema.sql')

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
    "MatchAssignments",
    "PlayerTeams"
]

for table_name in insertion_order:
    if table_name not in data_file.keys():
        print(f"table not found in data file: {table_name}")
        continue

    data = data_file[table_name]
    columns = data.columns.tolist()

    column_names = ', '.join(columns) # column names seperated by ', '
    column_value_placeholders = ', '.join(['%s'] * len(columns)) # %s for each column

    insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({column_value_placeholders})"

    print(insert_query)
    print()

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
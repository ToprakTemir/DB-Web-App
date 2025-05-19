import mysql.connector
from mysql.connector import Error
import sys

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="1234",
        database="ChessDB"
    )

def execute_sql_file(filename):
    db = get_db_connection()
    cur = db.cursor()

    with open(filename, 'r') as f:
        command = f.read()

    try:
        # Execute a statement; it can be single or multi.
        cur.execute(command)
    except Exception as e:
        print("Query execution failed:", e)

    results = []

    while cur.nextset():
        result_set = cur.fetchall()
        results.append(result_set)

    cur.close()
    db.commit()
    db.close()

    # Returns a 2D array with results[query_number][row_number]
    return results
        
def execute_sql_command(command):
    db = get_db_connection()
    cur = db.cursor()
    try:
        cur.execute(command)
    except Exception as e:
        print("Query execution failed:", e)
        return e

    results = []

    while cur.nextset():
        result_set = cur.fetchall()
        results.append(result_set)

    cur.close()
    db.commit()
    db.close()

    return results
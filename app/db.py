import mysql.connector
from mysql.connector import Error

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

    # Execute a statement; it can be single or multi.
    cur.execute(command)

    results = []

    while cur.nextset():
        result_set = cur.fetchall()
        results.append(result_set)

    cur.close()
    db.commit()
    db.close()

    # Returns a 2D array with results[query_number][row_number]
    return results
        

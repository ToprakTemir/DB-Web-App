import mysql.connector
from mysql.connector import Error

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="ChessDB"
    )

def execute_sql_file(filepath):
    with open(filepath, 'r') as file:
        sql = file.read()

    # Split by ';' and remove empty statements
    statements = [s.strip() for s in sql.split(';') if s.strip()]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
    except Error as e:
        print(f"Error executing SQL file {filepath}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
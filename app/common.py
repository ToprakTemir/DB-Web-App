import mysql.connector
from mysql.connector import Error
import bcrypt, re

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
        db.rollback()
        raise e

    results = []

    while cur.nextset():
        result_set = cur.fetchall()
        results.append(result_set)

    cur.close()
    db.commit()
    db.close()

    # Returns a 3D array with results[query_number][row_number][column_number]
    return results
        
def execute_sql_command(command):
    db = get_db_connection()
    cur = db.cursor()
    try:
        cur.execute(command)
    except Exception as e:
        print("Query execution failed:", e)
        db.rollback()
        raise e

    
    results = []
    result_set = cur.fetchall()
    results.append(result_set)

    while cur.nextset():
        result_set = cur.fetchall()
        results.append(result_set)

    cur.close()
    db.commit()
    db.close()

    return results

def encrypt_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()

    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')

def verify_password(plain_password, hashed_password):
    # Convert the hashed password back to bytes for comparison
    hashed_password_bytes = hashed_password.encode('utf-8')

    # Compare the plain password (hashed) with the stored hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)

def password_policy(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r'[A-Z]', password):
        return False, "Password must include at least one uppercase letter."

    if not re.search(r'[a-z]', password):
        return False, "Password must include at least one lowercase letter."

    if not re.search(r'\d', password):
        return False, "Password must include at least one digit."

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\\/\[\]~`+=]', password):
        return False, "Password must include at least one special character."

    return True, "Password is valid."
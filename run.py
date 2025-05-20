from app import create_app
from app import execute_sql_file
from app import seed_data

app = create_app()

app.secret_key = '@p1l2jckk-_12x-uszu)d%q##4x3n2hukp5(t8q)+1_o^d5mao'

if __name__ == '__main__':

    # execute seed_data() to refresh the database with initial data
    seed_data()

    execute_sql_file('app/sql/procedures.sql')
    execute_sql_file('app/sql/triggers.sql')

    app.run(debug=True)
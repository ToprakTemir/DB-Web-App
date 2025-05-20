from code import create_app
from code.db import execute_sql_file

app = create_app()

app.secret_key = '@p1l2jckk-_12x-uszu)d%q##4x3n2hukp5(t8q)+1_o^d5mao'

if __name__ == '__main__':
    execute_sql_file('code/procedures.sql')
    # execute_sql_file('sql/triggers.sql')
    execute_sql_file('code/views.sql')

    app.run(debug=True)
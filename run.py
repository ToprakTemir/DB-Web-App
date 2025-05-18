from app import create_app
from app.db import run_sql_file

app = create_app()

if __name__ == '__main__':

    run_sql_file('sql/triggers.sql')
    run_sql_file('sql/procedures.sql')
    run_sql_file('sql/seed_data.sql')
    run_sql_file('sql/views.sql')


    app.run(debug=True)
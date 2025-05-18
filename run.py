from app import create_app
from app.db import execute_sql_file

app = create_app()

if __name__ == '__main__':

    execute_sql_file('sql/schema.sql')
    execute_sql_file('sql/triggers.sql')
    execute_sql_file('sql/seed_data.sql')
    execute_sql_file('sql/views.sql')

    # sanity check
    app.run(debug=True)
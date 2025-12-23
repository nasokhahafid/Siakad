from app import create_app, db
from app.utils.db_importer import run_sql_file
import os

app = create_app()

# Check if the database is empty and run siakad.sql if necessary
with app.app_context():
    inspector = db.inspect(db.engine)
    if not inspector.get_table_names():
        sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'create_siakad_database.sql')
        run_sql_file(sql_file_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

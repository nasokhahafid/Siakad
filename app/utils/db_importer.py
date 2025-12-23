import os
from sqlalchemy import create_engine, text
from config import Config

def run_sql_file(sql_file_path):
    """
    Executes the SQL statements in the given file.

    :param sql_file_path: Path to the SQL file to execute.
    """
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")

    # Create a database engine
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    with engine.connect() as connection:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()

        # Execute SQL commands
        for statement in sql_commands.split(';'):
            if statement.strip():  # Skip empty statements
                connection.execute(text(statement))

if __name__ == "__main__":
    # Example usage
    run_sql_file("siakad.sql")
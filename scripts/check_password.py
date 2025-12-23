from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

hash_from_sql = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lLxQcK6m'

passwords_to_test = ['password', 'admin123', 'admin', '123456']

for p in passwords_to_test:
    is_match = bcrypt.check_password_hash(hash_from_sql, p)
    print(f"Testing '{p}': {'MATCH' if is_match else 'NO MATCH'}")

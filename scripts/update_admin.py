from app import create_app, db
from app.models.user import User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    admin = User.query.filter_by(nim='admin').first()
    if admin:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin.password = hashed_password
        db.session.commit()
        print("Admin password updated to 'admin123'")
    else:
        print("Admin user not found")

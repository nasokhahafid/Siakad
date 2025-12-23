from app import create_app
from app.models.user import User, db

app = create_app()

with app.app_context():
    try:
        # Test database connection
        users = User.query.all()
        print(f"✅ Database connection successful! Found {len(users)} users.")

        # Test creating a user
        test_user = User.query.filter_by(nim='test').first()
        if not test_user:
            print("ℹ️  Creating test user...")
            # Create test user for login testing
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(app)
            hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')

            test_user = User(
                nim='123456789',
                nama='Test User',
                email='@examptestle.com',
                program_studi='Teknik Informatika',
                password=hashed_password,
                role='mahasiswa'
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully!")
            print("   NIM: 123456789")
            print("   Password: password")
        else:
            print("ℹ️  Test user already exists")

    except Exception as e:
        print(f"❌ Database error: {e}")
        print("ℹ️  Make sure MySQL is running or use SQLite fallback")

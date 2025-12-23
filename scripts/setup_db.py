import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db, bcrypt
from app.models.user import User
from app.models.matkul import SystemSetting
from sqlalchemy import text

app = create_app()

def setup_database():
    with app.app_context():
        print("Checking database connection...")
        try:
            # Test connection
            db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            print("\nPlease make sure:")
            print("1. XAMPP (MySQL) is running.")
            print("2. Database 'siakad' has been created.")
            print("3. SQL URI in config.py is correct.")
            return

        # Ensure tables exist (optional, but good for safety)
        # db.create_all() 

        print("\nUpdating demo accounts with fresh hashes...")
        
        users_data = [
            {
                'nim': 'admin',
                'nama': 'Administrator',
                'email': 'admin@amikom.ac.id',
                'password': 'password',
                'role': 'admin',
                'prodi': 'Sistem Informasi'
            },
            {
                'nim': 'dosen1',
                'nama': 'Dr. Budi Santoso',
                'email': 'budi@amikom.ac.id',
                'password': 'password',
                'role': 'dosen',
                'prodi': 'Teknik Informatika'
            },
            {
                'nim': 'mahasiswa1',
                'nama': 'Ahmad Fauzi',
                'email': 'ahmad@student.amikom.ac.id',
                'password': 'password',
                'role': 'mahasiswa',
                'prodi': 'Teknik Informatika'
            }
        ]

        for u_data in users_data:
            user = User.query.filter_by(nim=u_data['nim']).first()
            hashed_pw = bcrypt.generate_password_hash(u_data['password']).decode('utf-8')
            
            if user:
                print(f"Updating user: {u_data['nim']}...")
                user.password = hashed_pw
                user.nama = u_data['nama']
                user.email = u_data['email']
                user.role = u_data['role']
                user.program_studi = u_data['prodi']
            else:
                print(f"Creating user: {u_data['nim']}...")
                new_user = User(
                    nim=u_data['nim'],
                    nama=u_data['nama'],
                    email=u_data['email'],
                    password=hashed_pw,
                    role=u_data['role'],
                    program_studi=u_data['prodi']
                )
                db.session.add(new_user)
        
        # Ensure advisor relationship for mahasiswa1
        mahasiswa = User.query.filter_by(nim='mahasiswa1').first()
        dosen = User.query.filter_by(nim='dosen1').first()
        if mahasiswa and dosen:
            mahasiswa.advisor_id = dosen.id

        # Setup default system settings if missing
        settings = [
            ('system_name', 'SIAKAD'),
            ('max_file_size', '10'),
            ('backup_frequency', 'daily')
        ]
        for key, val in settings:
            if not SystemSetting.query.filter_by(setting_key=key).first():
                db.session.add(SystemSetting(setting_key=key, setting_value=val))

        db.session.commit()
        print("\nSUCCESS: All demo accounts are ready to use!")
        print("-" * 30)
        print("Username: admin, dosen1, mahasiswa1")
        print("Password: password")
        print("-" * 30)

if __name__ == "__main__":
    setup_database()

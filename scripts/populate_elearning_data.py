from app import create_app, db
from app.models.user import User
from app.models.matkul import Course, Material, Video, Grade, Submission
from flask_bcrypt import Bcrypt
import os

app = create_app()

def populate_elearning_data():
    with app.app_context():
        try:
            # Create bcrypt instance
            bcrypt = Bcrypt(app)

            # Create test lecturer if not exists
            lecturer = User.query.filter_by(nim='lecturer001').first()
            if not lecturer:
                print("Creating test lecturer...")
                hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
                lecturer = User(
                    nim='lecturer001',
                    nama='Dr. Budi Santoso',
                    email='budi.santoso@amikom.ac.id',
                    program_studi='Teknik Informatika',
                    password=hashed_password,
                    role='dosen'
                )
                db.session.add(lecturer)
                db.session.commit()
                print("DONE: Lecturer created")

            # Create test student if not exists
            student = User.query.filter_by(nim='123456789').first()
            if not student:
                print("Creating test student...")
                hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
                student = User(
                    nim='123456789',
                    nama='Test User',
                    email='test@example.com',
                    program_studi='Teknik Informatika',
                    password=hashed_password,
                    role='mahasiswa'
                )
                db.session.add(student)
                db.session.commit()
                print("DONE: Student created")

            # Create courses
            courses_data = [
                {'kode': 'IF201', 'nama': 'Pemrograman Web', 'sks': 3, 'semester': 5},
                {'kode': 'IF202', 'nama': 'Basis Data', 'sks': 3, 'semester': 5},
                {'kode': 'IF203', 'nama': 'Jaringan Komputer', 'sks': 3, 'semester': 5},
                {'kode': 'IF204', 'nama': 'Keamanan Informasi', 'sks': 3, 'semester': 5},
            ]

            for course_data in courses_data:
                course = Course.query.filter_by(kode=course_data['kode']).first()
                if not course:
                    print(f"Creating course: {course_data['nama']}...")
                    course = Course(
                        kode=course_data['kode'],
                        nama=course_data['nama'],
                        sks=course_data['sks'],
                        semester=course_data['semester'],
                        dosen_id=lecturer.id
                    )
                    db.session.add(course)
                    db.session.commit()
                    print(f"DONE: Course {course_data['nama']} created")

                # Check if materials exist for this course
                existing_materials = Material.query.filter_by(course_id=course.id).count()
                if existing_materials == 0:
                    print(f"Adding materials for course: {course_data['nama']}...")
                    # Add materials for each course
                    materials_data = [
                        {
                            'judul': f'Materi Dasar {course_data["nama"]}',
                            'deskripsi': f'Pengantar dan konsep dasar {course_data["nama"]}',
                            'file_path': f'/static/materials/{course_data["kode"]}_materi1.pdf',
                            'tipe': 'pdf',
                            'minggu': 1
                        },
                        {
                            'judul': f'Praktikum {course_data["nama"]} Minggu 1',
                            'deskripsi': f'Latihan praktikum untuk {course_data["nama"]}',
                            'file_path': f'/static/materials/{course_data["kode"]}_praktikum1.pdf',
                            'tipe': 'pdf',
                            'minggu': 1
                        },
                        {
                            'judul': f'Materi Lanjutan {course_data["nama"]}',
                            'deskripsi': f'Konsep lanjutan {course_data["nama"]}',
                            'file_path': f'/static/materials/{course_data["kode"]}_materi2.pdf',
                            'tipe': 'pdf',
                            'minggu': 2
                        }
                    ]

                    for material_data in materials_data:
                        material = Material(
                            course_id=course.id,
                            judul=material_data['judul'],
                            deskripsi=material_data['deskripsi'],
                            file_path=material_data['file_path'],
                            tipe=material_data['tipe'],
                            minggu=material_data['minggu'],
                            uploaded_by=lecturer.id
                        )
                        db.session.add(material)
                    print(f"DONE: Materials added for {course_data['nama']}")

                # Check if videos exist for this course
                existing_videos = Video.query.filter_by(course_id=course.id).count()
                if existing_videos == 0:
                    print(f"Adding videos for course: {course_data['nama']}...")
                    # Add videos for each course
                    videos_data = [
                        {
                            'judul': f'Video Pengantar {course_data["nama"]}',
                            'deskripsi': f'Video pengantar untuk mata kuliah {course_data["nama"]}',
                            'video_path': f'/static/videos/{course_data["kode"]}_intro.mp4',
                            'durasi': 45,
                            'minggu': 1
                        },
                        {
                            'judul': f'Tutorial {course_data["nama"]} Part 1',
                            'deskripsi': f'Tutorial praktis {course_data["nama"]} bagian 1',
                            'video_path': f'/static/videos/{course_data["kode"]}_tutorial1.mp4',
                            'durasi': 60,
                            'minggu': 2
                        }
                    ]

                    for video_data in videos_data:
                        video = Video(
                            course_id=course.id,
                            judul=video_data['judul'],
                            deskripsi=video_data['deskripsi'],
                            video_path=video_data['video_path'],
                            durasi=video_data['durasi'],
                            minggu=video_data['minggu'],
                            uploaded_by=lecturer.id
                        )
                        db.session.add(video)
                    print(f"DONE: Videos added for {course_data['nama']}")

                db.session.commit()

            # Add sample grades for the student
            for course in Course.query.all():
                grade = Grade.query.filter_by(student_id=student.id, course_id=course.id).first()
                if not grade:
                    grade = Grade(
                        student_id=student.id,
                        course_id=course.id,
                        nilai=85.0,
                        bobot=course.sks,
                        grade='A',
                        semester=course.semester
                    )
                    db.session.add(grade)

            db.session.commit()
            print("DONE: Sample grades added")

            # Add sample submissions
            sample_submissions = [
                {
                    'judul': 'Tugas HTML & CSS',
                    'deskripsi': 'Implementasi halaman web responsif',
                    'status': 'pending'
                },
                {
                    'judul': 'Tugas Database Design',
                    'deskripsi': 'Perancangan skema database',
                    'status': 'approved',
                    'nilai': 90.0
                }
            ]

            for submission_data in sample_submissions:
                submission = Submission(
                    student_id=student.id,
                    course_id=Course.query.filter_by(kode='IF201').first().id,
                    judul=submission_data['judul'],
                    deskripsi=submission_data['deskripsi'],
                    status=submission_data['status'],
                    nilai=submission_data.get('nilai')
                )
                db.session.add(submission)

            db.session.commit()
            print("DONE: Sample submissions added")

            print("\nSUCCESS: E-Learning data populated successfully!")
            print("\nTest Accounts:")
            print("Student: NIM=123456789, Password=password")
            print("Lecturer: NIM=lecturer001, Password=password")

        except Exception as e:
            print(f"ERROR: Error populating data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    populate_elearning_data()

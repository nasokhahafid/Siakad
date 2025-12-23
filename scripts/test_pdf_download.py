#!/usr/bin/env python3
"""
Test script to verify KHS PDF download functionality
"""
import requests
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from app import create_app, db
from app.models.user import User
from app.models.matkul import Course, Grade

def test_pdf_generation():
    """Test PDF generation without authentication"""
    app = create_app()

    with app.app_context():
        # Create test user if not exists
        test_user = User.query.filter_by(nim='123456789').first()
        if not test_user:
            # Hash the password using bcrypt
            bcrypt = Bcrypt(app)
            hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')

            test_user = User(
                nim='123456789',
                nama='Test Student',
                email='test@student.com',
                program_studi='Teknik Informatika',
                password=hashed_password,
                role='mahasiswa'
            )
            db.session.add(test_user)
            db.session.commit()

        # Create test course if not exists
        test_course = Course.query.filter_by(kode='IF101').first()
        if not test_course:
            test_course = Course(
                kode='IF101',
                nama='Pemrograman Dasar',
                sks=3,
                semester=1,
                dosen_id=test_user.id
            )
            db.session.add(test_course)
            db.session.commit()

        # Create test grades if not exists
        existing_grades = Grade.query.filter_by(student_id=test_user.id).count()
        if existing_grades == 0:
            # Create grades for multiple semesters
            grades_data = [
                {'nilai': 85, 'bobot': 3.0, 'grade': 'A', 'semester': 1},
                {'nilai': 82, 'bobot': 3.0, 'grade': 'A', 'semester': 1},
                {'nilai': 78, 'bobot': 3.0, 'grade': 'B', 'semester': 1},
                {'nilai': 88, 'bobot': 3.0, 'grade': 'A', 'semester': 2},
                {'nilai': 80, 'bobot': 3.0, 'grade': 'A', 'semester': 2},
                {'nilai': 75, 'bobot': 3.0, 'grade': 'B', 'semester': 3},
                {'nilai': 85, 'bobot': 3.0, 'grade': 'A', 'semester': 4},
                {'nilai': 82, 'bobot': 3.0, 'grade': 'A', 'semester': 4},
                {'nilai': 78, 'bobot': 3.0, 'grade': 'B', 'semester': 4},
                {'nilai': 88, 'bobot': 3.0, 'grade': 'A', 'semester': 5},
                {'nilai': 80, 'bobot': 3.0, 'grade': 'A', 'semester': 5},
                {'nilai': 75, 'bobot': 3.0, 'grade': 'B', 'semester': 5},
            ]

            for grade_data in grades_data:
                grade = Grade(
                    student_id=test_user.id,
                    course_id=test_course.id,
                    nilai=grade_data['nilai'],
                    bobot=grade_data['bobot'],
                    grade=grade_data['grade'],
                    semester=grade_data['semester']
                )
                db.session.add(grade)
            db.session.commit()

        print("Test data created successfully!")

        # Test PDF generation using test client
        with app.test_client() as client:
            # First, login the user
            login_response = client.post('/login', data={
                'username': '123456789',
                'password': 'password123'
            }, follow_redirects=True)

            if login_response.status_code != 200:
                print("Login failed!")
                return False

            # Now test the PDF download
            try:
                pdf_response = client.get('/akademik/khs/download')

                if pdf_response.status_code == 200:
                    print("PDF generation successful!")

                    # Save the PDF to test file
                    with open('test_khs.pdf', 'wb') as f:
                        f.write(pdf_response.data)

                    print("PDF saved as 'test_khs.pdf'")
                    print(f"PDF size: {len(pdf_response.data)} bytes")
                    print(f"Content-Type: {pdf_response.content_type}")

                    return True
                else:
                    print(f"PDF generation failed with status: {pdf_response.status_code}")
                    print(f"Response: {pdf_response.data.decode('utf-8', errors='ignore')}")
                    return False

            except Exception as e:
                print(f"PDF generation failed: {str(e)}")
                return False

if __name__ == '__main__':
    success = test_pdf_generation()
    if success:
        print("\n✅ PDF generation test PASSED")
    else:
        print("\n❌ PDF generation test FAILED")

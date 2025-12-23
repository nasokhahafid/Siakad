from datetime import datetime
from flask_login import UserMixin
from .. import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    program_studi = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='mahasiswa')  # mahasiswa, dosen, admin
    advisor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    advisor = db.relationship('User', remote_side=[id], backref='advisees')
    grades = db.relationship('Grade', backref='student', lazy=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)

    def __repr__(self):
        return f"User('{self.nim}', '{self.nama}', '{self.email}')"

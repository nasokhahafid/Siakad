from datetime import datetime
from .. import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    sks = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    dosen_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    dosen = db.relationship('User', backref='courses_taught', lazy=True)
    grades = db.relationship('Grade', backref='course', lazy=True)
    materials = db.relationship('Material', backref='course', lazy=True)
    videos = db.relationship('Video', backref='course', lazy=True)
    submissions = db.relationship('Submission', backref='course', lazy=True)

    def __repr__(self):
        return f"Course('{self.kode}', '{self.nama}')"

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    nilai = db.Column(db.Float, nullable=False)
    bobot = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Grade('{self.student_id}', '{self.course_id}', '{self.nilai}')"

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    tipe = db.Column(db.String(20))  # pdf, pptx, docx, dll
    minggu = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    uploader = db.relationship('User', backref='uploaded_materials', lazy=True)

    def __repr__(self):
        return f"Material('{self.judul}', '{self.course_id}')"

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text)
    video_path = db.Column(db.String(500))
    durasi = db.Column(db.Integer)  # dalam menit
    minggu = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    uploader = db.relationship('User', backref='uploaded_videos', lazy=True)

    def __repr__(self):
        return f"Video('{self.judul}', '{self.course_id}')"

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    nilai = db.Column(db.Float)
    komentar = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Submission('{self.judul}', '{self.student_id}', '{self.status}')"

class KRS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    tahun_ajaran = db.Column(db.String(20), nullable=False)  # e.g., "2023/2024"
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='krs_entries', lazy=True)
    course = db.relationship('Course', backref='krs_entries', lazy=True)
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_krs', lazy=True)

    def __repr__(self):
        return f"KRS('{self.student_id}', '{self.course_id}', '{self.semester}', '{self.status}')"

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    hari = db.Column(db.String(10), nullable=False)  # e.g., 'Senin', 'Selasa', etc.
    waktu_mulai = db.Column(db.String(5), nullable=False)  # e.g., '08:00'
    waktu_selesai = db.Column(db.String(5), nullable=False)  # e.g., '10:00'
    ruangan = db.Column(db.String(50), nullable=False)  # e.g., 'Lab Komputer 1'
    semester = db.Column(db.Integer, nullable=False)
    tahun_ajaran = db.Column(db.String(20), nullable=False)  # e.g., "2023/2024"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', backref='schedules', lazy=True)

    def __repr__(self):
        return f"Schedule('{self.course.nama}', '{self.hari}', '{self.waktu_mulai}-{self.waktu_selesai}')"

class VideoWatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    watch_time = db.Column(db.Integer, default=0)  # dalam detik
    total_duration = db.Column(db.Integer, default=0)  # dalam detik
    completed = db.Column(db.Boolean, default=False)
    last_watched = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User', backref='video_watches', lazy=True)
    video = db.relationship('Video', backref='watches', lazy=True)

    def __repr__(self):
        return f"VideoWatch('{self.student.nama}', '{self.video.judul}', '{self.watch_time}s')"

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(500))
    replies_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', backref='forum_posts', lazy=True)
    student = db.relationship('User', backref='forum_posts', lazy=True)

    def __repr__(self):
        return f"ForumPost('{self.title}', '{self.student.nama}')"

class ForumReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    post = db.relationship('ForumPost', lazy=True)
    student = db.relationship('User', backref='forum_replies', lazy=True)

    def __repr__(self):
        return f"ForumReply('{self.student.nama}', '{self.post.title}')"

class LetterSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    letter_type = db.Column(db.String(50), nullable=False)  # 'certificate', 'transcript', 'leave', 'recommendation', etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    file_path = db.Column(db.String(500))
    notes = db.Column(db.Text)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='letter_submissions', lazy=True)
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_letters', lazy=True)

    def __repr__(self):
        return f"LetterSubmission('{self.student.nama}', '{self.letter_type}', '{self.status}')"

class InternshipApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    perusahaan = db.Column(db.String(200), nullable=False)
    posisi = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='internship_applications', lazy=True)

class ThesisApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    judul_skripsi = db.Column(db.String(500), nullable=False)
    peminatan = db.Column(db.String(100), nullable=False)
    abstrak = db.Column(db.Text, nullable=False)
    dosen_pref = db.Column(db.String(200))
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='thesis_applications', lazy=True)

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

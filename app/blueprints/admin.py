from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.models.matkul import Course, Grade, Submission, SystemSetting
from app import db, bcrypt

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    total_users = User.query.count()
    total_students = User.query.filter_by(role='mahasiswa').count()
    total_lecturers = User.query.filter_by(role='dosen').count()
    total_courses = Course.query.count()
    new_users = User.query.order_by(User.created_at.desc()).limit(3).all()
    new_courses = Course.query.order_by(Course.id.desc()).limit(2).all()
    
    recent_activities = []
    for u in new_users:
        recent_activities.append({'type': 'user', 'description': f'User baru: {u.nama} ({u.role})', 'time': u.created_at.strftime('%d %b')})
    for c in new_courses:
        recent_activities.append({'type': 'course', 'description': f'Matkul baru: {c.nama}', 'time': 'Baru'})
    return render_template('dashboard_admin.html',
                         total_users=total_users,
                         total_students=total_students,
                         total_lecturers=total_lecturers,
                         total_courses=total_courses,
                         recent_activities=recent_activities)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nim = request.form.get('nim')
        nama = request.form.get('nama')
        email = request.form.get('email')
        program_studi = request.form.get('program_studi')
        role = request.form.get('role')
        password = request.form.get('password')
        if not all([nim, nama, email, program_studi, role, password]):
            flash('Semua field harus diisi.', 'error')
            return redirect(url_for('admin.add_user'))
        existing_user = User.query.filter((User.nim == nim) | (User.email == email)).first()
        if existing_user:
            flash('NIM atau email sudah terdaftar.', 'error')
            return redirect(url_for('admin.add_user'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(nim=nim, nama=nama, email=email, program_studi=program_studi, password=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        flash('User berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.add_user'))
    return render_template('admin_add_user.html')

@admin_bp.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        kode = request.form.get('kode')
        nama = request.form.get('nama')
        sks = request.form.get('sks')
        semester = request.form.get('semester')
        dosen_nim = request.form.get('dosen_nim')
        if not all([kode, nama, sks, semester, dosen_nim]):
            flash('Semua field harus diisi.', 'error')
            return redirect(url_for('admin.add_course'))
        dosen = User.query.filter_by(nim=dosen_nim, role='dosen').first()
        if not dosen:
            flash('Dosen dengan NIM tersebut tidak ditemukan.', 'error')
            return redirect(url_for('admin.add_course'))
        existing_course = Course.query.filter_by(kode=kode).first()
        if existing_course:
            flash('Kode mata kuliah sudah ada.', 'error')
            return redirect(url_for('admin.add_course'))
        course = Course(kode=kode, nama=nama, sks=int(sks), semester=int(semester), dosen_id=dosen.id)
        db.session.add(course)
        db.session.commit()
        flash('Mata kuliah berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.add_course'))
    lecturers = User.query.filter_by(role='dosen').all()
    return render_template('admin_add_course.html', lecturers=lecturers)

@admin_bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    total_users = User.query.count()
    total_students = User.query.filter_by(role='mahasiswa').count()
    total_lecturers = User.query.filter_by(role='dosen').count()
    total_courses = Course.query.count()
    total_submissions = Submission.query.count()
    recent_submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(10).all()
    courses_stats = []
    courses = Course.query.all()
    for course in courses:
        student_count = Grade.query.filter_by(course_id=course.id).count()
        submission_count = Submission.query.filter_by(course_id=course.id).count()
        courses_stats.append({
            'course': course,
            'student_count': student_count,
            'submission_count': submission_count
        })
    return render_template('admin_reports.html',
                         total_users=total_users,
                         total_students=total_students,
                         total_lecturers=total_lecturers,
                         total_courses=total_courses,
                         total_submissions=total_submissions,
                         recent_submissions=recent_submissions,
                         courses_stats=courses_stats)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        for key in ['system_name', 'max_file_size', 'backup_frequency']:
            val = request.form.get(key)
            if val:
                setting = SystemSetting.query.filter_by(setting_key=key).first()
                if setting:
                    setting.setting_value = val
                else:
                    new_setting = SystemSetting(setting_key=key, setting_value=val)
                    db.session.add(new_setting)
        db.session.commit()
        flash('Pengaturan berhasil diperbarui!', 'success')
        return redirect(url_for('admin.settings'))
        
    settings_obj = SystemSetting.query.all()
    current_settings = {s.setting_key: s.setting_value for s in settings_obj}
    return render_template('admin_settings.html', settings=current_settings)

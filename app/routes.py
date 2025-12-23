from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from .models.user import User
from .models.matkul import Course, Grade, Material, Video, Submission, KRS, ForumPost, ForumReply, Schedule, VideoWatch
from . import db, bcrypt
from flask_login import login_user, login_required, logout_user, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'mahasiswa':
            return redirect(url_for('main.dashboard_mahasiswa'))
        elif current_user.role == 'dosen':
            return redirect(url_for('main.dashboard_dosen'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.dashboard_mahasiswa'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nim = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(nim=nim).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login berhasil!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login gagal. Periksa NIM dan password.', 'error')
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nim = request.form.get('nim')
        nama = request.form.get('nama')
        email = request.form.get('email')
        program_studi = request.form.get('program_studi')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok.', 'error')
            return redirect(url_for('main.register'))
        existing_user = User.query.filter((User.nim == nim) | (User.email == email)).first()
        if existing_user:
            flash('NIM atau email sudah terdaftar.', 'error')
            return redirect(url_for('main.register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(nim=nim, nama=nama, email=email, program_studi=program_studi, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        flash('Link reset password telah dikirim ke email Anda.', 'info')
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html')

@main_bp.route('/dashboard/mahasiswa')
@login_required
def dashboard_mahasiswa():
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))
    courses = Course.query.all()
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    total_sks = sum(grade.bobot for grade in grades)
    total_nilai_bobot = sum(grade.nilai * grade.bobot for grade in grades)
    ipk = total_nilai_bobot / total_sks if total_sks > 0 else 0
    # Fetch today's schedule (e.g., today is Senin for demo if none found)
    import datetime
    days_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    today_name = days_map[datetime.datetime.now().weekday()]
    today_schedule = Schedule.query.filter_by(hari=today_name).all()
    
    # Real activities from DB
    submissions = Submission.query.filter_by(student_id=current_user.id).order_by(Submission.submitted_at.desc()).limit(3).all()
    posts = ForumPost.query.filter_by(student_id=current_user.id).order_by(ForumPost.created_at.desc()).limit(2).all()
    
    recent_activities = []
    for s in submissions:
        recent_activities.append({
            'type': 'upload',
            'description': f'Tugas {s.judul} dikumpulkan',
            'time': s.submitted_at.strftime('%d %b %H:%M')
        })
    for p in posts:
        recent_activities.append({
            'type': 'forum',
            'description': f'Posting di forum: {p.title}',
            'time': p.created_at.strftime('%d %b %H:%M')
        })
    # Calculate Presence/Progress
    total_videos = Video.query.count() # Simplified, should be based on enrolled courses
    watched_videos = VideoWatch.query.filter_by(student_id=current_user.id, completed=True).count()
    presence_percent = round((watched_videos / total_videos * 100), 1) if total_videos > 0 else 0

    return render_template('dashboard_mahasiswa.html',
                         courses=courses,
                         grades=grades,
                         ipk=round(ipk, 2),
                         total_sks=total_sks,
                         presence_percent=presence_percent,
                         recent_activities=recent_activities,
                         today_schedule=today_schedule)

@main_bp.route('/dashboard/dosen')
@login_required
def dashboard_dosen():
    if current_user.role != 'dosen':
        return redirect(url_for('main.index'))
    courses = Course.query.filter_by(dosen_id=current_user.id).all()
    course_ids = [c.id for c in courses]
    
    # Real stats
    new_submissions_count = Submission.query.filter(Submission.course_id.in_(course_ids), Submission.status == 'pending').count()
    total_students_count = db.session.query(db.func.count(db.distinct(Grade.student_id))).filter(Grade.course_id.in_(course_ids)).scalar() or 0
    
    # Per course student counts
    course_stats = []
    for c in courses:
        count = Grade.query.filter_by(course_id=c.id).count()
        course_stats.append({
            'id': c.id,
            'kode': c.kode,
            'nama': c.nama,
            'sks': c.sks,
            'student_count': count
        })

    # Recent unrated submissions
    pending_submissions = Submission.query.filter(Submission.course_id.in_(course_ids), Submission.status == 'pending').order_by(Submission.submitted_at.desc()).limit(3).all()
    
    # Today's teaching schedule
    import datetime
    days_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    today_name = days_map[datetime.datetime.now().weekday()]
    teaching_schedule = Schedule.query.filter(Schedule.course_id.in_(course_ids), Schedule.hari == today_name).all()

    return render_template('dashboard_dosen.html', 
                         courses=courses,
                         course_stats=course_stats,
                         new_submissions_count=new_submissions_count,
                         total_students_count=total_students_count,
                         pending_submissions=pending_submissions,
                         teaching_schedule=teaching_schedule)

@main_bp.route('/dosen/courses')
@login_required
def dosen_courses():
    if current_user.role != 'dosen':
        return redirect(url_for('main.index'))
    courses = Course.query.filter_by(dosen_id=current_user.id).all()
    course_ids = [c.id for c in courses]
    
    # Real stats
    new_submissions_count = Submission.query.filter(Submission.course_id.in_(course_ids), Submission.status == 'pending').count()
    total_students_count = db.session.query(db.func.count(db.distinct(Grade.student_id))).filter(Grade.course_id.in_(course_ids)).scalar() or 0
    
    # Recent unrated submissions
    pending_submissions = Submission.query.filter(Submission.course_id.in_(course_ids), Submission.status == 'pending').order_by(Submission.submitted_at.desc()).limit(3).all()
    
    # Today's teaching schedule
    import datetime
    days_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    today_name = days_map[datetime.datetime.now().weekday()]
    teaching_schedule = Schedule.query.filter(Schedule.course_id.in_(course_ids), Schedule.hari == today_name).all()

    return render_template('dashboard_dosen.html', 
                         courses=courses,
                         new_submissions_count=new_submissions_count,
                         total_students_count=total_students_count,
                         pending_submissions=pending_submissions,
                         teaching_schedule=teaching_schedule)

@main_bp.route('/dosen/submissions')
@login_required
def dosen_submissions():
    if current_user.role != 'dosen':
        return redirect(url_for('main.index'))
    courses = Course.query.filter_by(dosen_id=current_user.id).all()
    course_ids = [c.id for c in courses]
    submissions = Submission.query.filter(Submission.course_id.in_(course_ids)).order_by(Submission.submitted_at.desc()).all()
    return render_template('dosen_submissions.html', submissions=submissions, courses=courses)

# API Routes
@main_bp.route('/api/material/<int:material_id>/download', methods=['POST'])
@login_required
def download_material(material_id):
    material = Material.query.get_or_404(material_id)
    return jsonify({
        'status': 'success',
        'message': f'Download {material.judul} berhasil',
        'file_url': material.file_path
    })

@main_bp.route('/api/submission/<int:submission_id>/status', methods=['POST'])
@login_required
def update_submission_status(submission_id):
    if current_user.role != 'dosen':
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    submission = Submission.query.get_or_404(submission_id)
    data = request.get_json()
    submission.status = data.get('status', submission.status)
    submission.nilai = data.get('nilai', submission.nilai)
    submission.komentar = data.get('komentar', submission.komentar)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Status berhasil diperbarui'})

@main_bp.route('/api/video/<int:video_id>/watch', methods=['POST'])
@login_required
def track_video_watch(video_id):
    data = request.get_json()
    watch_time = data.get('watch_time', 0)
    total_duration = data.get('total_duration', 0)
    return jsonify({
        'status': 'success',
        'message': 'Video watch time tracked',
        'progress': (watch_time / total_duration * 100) if total_duration > 0 else 0
    })

@main_bp.route('/api/forum/post', methods=['POST'])
@login_required
def create_forum_post():
    if current_user.role != 'mahasiswa':
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    data = request.get_json()
    course_kode = data.get('course')
    title = data.get('title')
    content = data.get('content')
    course = Course.query.filter_by(kode=course_kode).first()
    if not course:
        return jsonify({'status': 'error', 'message': 'Course not found'})
    forum_post = ForumPost(student_id=current_user.id, course_id=course.id, title=title, content=content)
    db.session.add(forum_post)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': 'Forum post created successfully',
        'post': {
            'id': forum_post.id,
            'title': forum_post.title,
            'author': current_user.nama,
            'course': course.nama,
            'time': forum_post.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@main_bp.route('/api/forum/reply', methods=['POST'])
@login_required
def create_forum_reply():
    if current_user.role != 'mahasiswa':
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content')
    forum_reply = ForumReply(student_id=current_user.id, post_id=post_id, content=content)
    db.session.add(forum_reply)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': 'Forum reply created successfully',
        'reply': {
            'id': forum_reply.id,
            'content': forum_reply.content,
            'author': current_user.nama,
            'time': forum_reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

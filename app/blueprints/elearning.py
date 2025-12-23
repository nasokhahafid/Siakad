from flask import Blueprint, render_template, redirect, url_for, jsonify, request, flash, current_app
from flask_login import login_required, current_user
from app.models.matkul import Course, Material, Video, VideoWatch, KRS, Grade, Submission, ForumPost, ForumReply
from app import db
import os


elearning_bp = Blueprint('elearning', __name__, url_prefix='/elearning')

@elearning_bp.route('/materi')
@login_required
def materi():
    if current_user.role not in ['mahasiswa', 'dosen']:
        return redirect(url_for('main.index'))

    courses = Course.query.all()
    materials = Material.query.order_by(Material.minggu, Material.created_at).all()
    videos = Video.query.order_by(Video.minggu, Video.created_at).all()

    materials_by_week = {}
    for material in materials:
        week = material.minggu or 1
        if week not in materials_by_week:
            materials_by_week[week] = []
        materials_by_week[week].append(material)

    videos_by_week = {}
    for video in videos:
        week = video.minggu or 1
        if week not in videos_by_week:
            videos_by_week[week] = []
        videos_by_week[week].append(video)

    return render_template('elearning_materi.html',
                         courses=courses,
                         materials_by_week=materials_by_week,
                         videos_by_week=videos_by_week)

@elearning_bp.route('/video', defaults={'video_id': None})
@elearning_bp.route('/video/<int:video_id>')
@login_required
def video(video_id):
    if current_user.role not in ['mahasiswa', 'dosen']:
        return redirect(url_for('main.index'))

    # Database videos
    videos_db = Video.query.order_by(Video.minggu, Video.created_at).all()

    # Filesystem fallback videos (from app/static/videos)
    video_dir = os.path.join(current_app.root_path, 'static', 'videos')
    fs_videos = []
    if os.path.isdir(video_dir):
        for f in sorted(os.listdir(video_dir)):
            if f.lower().endswith(('.mp4', '.webm', '.ogg', '.m4v')):
                fs_videos.append(f)

    playlist = []
    current_video_url = None
    current_title = None

    if videos_db:
        # Build playlist from DB
        for v in videos_db:
            # Ensure path attribute name is correct (model uses video_path)
            path = v.video_path or ''
            # If stored path is like 'videos/xxx.mp4', use it; else prepend 'videos/' if needed
            if not path.startswith('videos/') and not path.startswith('http'):
                path = f"videos/{path}"
            url = url_for('static', filename=path)
            playlist.append({'title': v.judul or os.path.basename(path), 'url': url, 'id': v.id})
        # Determine current video
        if video_id:
            main_video = Video.query.get_or_404(video_id)
            path = main_video.video_path or ''
            if not path.startswith('videos/') and not path.startswith('http'):
                path = f"videos/{path}"
            current_video_url = url_for('static', filename=path)
            current_title = main_video.judul or os.path.basename(path)
        else:
            current_video_url = playlist[0]['url']
            current_title = playlist[0]['title']
    elif fs_videos:
        # Build playlist from filesystem
        for f in fs_videos:
            url = url_for('static', filename=f'videos/{f}')
            playlist.append({'title': os.path.splitext(f)[0], 'url': url, 'id': None})
        current_video_url = playlist[0]['url']
        current_title = playlist[0]['title']
    else:
        # No videos available
        playlist = []
        current_video_url = None
        current_title = None

    # Get video watch progress for current user (DB videos only)
    video_watches = VideoWatch.query.filter_by(student_id=current_user.id).all()
    watch_progress = {watch.video_id: watch for watch in video_watches}

    return render_template('elearning_video.html',
                         playlist=playlist,
                         current_video_url=current_video_url,
                         current_title=current_title,
                         watch_progress=watch_progress)

@elearning_bp.route('/download')
@login_required
def download():
    if current_user.role not in ['mahasiswa', 'dosen']:
        return redirect(url_for('main.index'))

    # Materials from DB
    courses = Course.query.all()
    materials = Material.query.all()

    # Filesystem modules from app/static/modul
    modul_dir = os.path.join(current_app.root_path, 'static', 'modul')
    modul_files = []
    if os.path.isdir(modul_dir):
        for f in sorted(os.listdir(modul_dir)):
            # Allow common doc types and pdf
            if f.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.zip')):
                modul_files.append({
                    'name': f,
                    'url': url_for('static', filename=f'modul/{f}')
                })

    return render_template('elearning_download.html', courses=courses, materials=materials, modul_files=modul_files)

@elearning_bp.route('/progress')
@login_required
def progress():
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))

    # Get courses the student is enrolled in
    krs_entries = KRS.query.filter_by(student_id=current_user.id).all()
    if krs_entries:
        courses = [krs.course for krs in krs_entries if krs.course]
    else:
        # Fallback to courses from grades
        grades = Grade.query.filter_by(student_id=current_user.id).all()
        course_ids = list(set(grade.course_id for grade in grades))
        courses = Course.query.filter(Course.id.in_(course_ids)).all() if course_ids else []

    progress_data = []
    chart_data = {
        'labels': [],
        'datasets': [{
            'label': 'Progress Belajar (%)',
            'data': [],
            'backgroundColor': 'rgba(54, 162, 235, 0.6)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }]
    }

    for course in courses:
        video_total = Video.query.filter_by(course_id=course.id).count()
        watched_video_ids = [watch.video_id for watch in VideoWatch.query.filter_by(student_id=current_user.id).all()]
        video_completed = Video.query.filter(Video.id.in_(watched_video_ids), Video.course_id == course.id).count() if watched_video_ids else 0
        
        total_items = video_total
        completed_items = video_completed
        
        progress_percentage = int((completed_items / total_items * 100) if total_items > 0 else 0)

        progress_data.append({
            'nama': course.nama,
            'progress': progress_percentage,
        })
        
        chart_data['labels'].append(course.nama)
        chart_data['datasets'][0]['data'].append(progress_percentage)

    # Fallback dummy data to avoid empty chart
    if not chart_data['labels']:
        chart_data['labels'] = ['Contoh 1', 'Contoh 2']
        chart_data['datasets'][0]['data'] = [40, 70]

    return render_template('elearning_progress.html', progress_data=progress_data, chart_data=chart_data)

@elearning_bp.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    if current_user.role not in ['mahasiswa', 'dosen']:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        course_id = request.form.get('course_id')

        if not all([title, content, course_id]):
            flash('Semua field harus diisi.', 'error')
            return redirect(url_for('elearning.forum'))

        post = ForumPost(
            student_id=current_user.id,
            course_id=course_id,
            title=title,
            content=content
        )
        db.session.add(post)
        db.session.commit()
        flash('Postingan berhasil dibuat!', 'success')
        return redirect(url_for('elearning.forum'))

    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
    courses = Course.query.all()
    return render_template('elearning_forum.html', forum_posts=posts, courses=courses)

@elearning_bp.route('/forum/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def forum_post(post_id):
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))

    post = ForumPost.query.get_or_404(post_id)

    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Balasan tidak boleh kosong.', 'error')
            return redirect(url_for('elearning.forum_post', post_id=post_id))

        reply = ForumReply(
            student_id=current_user.id,
            post_id=post_id,
            content=content
        )
        db.session.add(reply)
        db.session.commit()
        flash('Balasan berhasil dikirim!', 'success')
        return redirect(url_for('elearning.forum_post', post_id=post_id))

    replies = ForumReply.query.filter_by(post_id=post.id).order_by(ForumReply.created_at.asc()).all()
    return render_template('elearning_forum_post.html', post=post, replies=replies)

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.matkul import Course, Submission, LetterSubmission, InternshipApplication, ThesisApplication
from app import db
from datetime import datetime
import os

pengajuan_bp = Blueprint('pengajuan', __name__, url_prefix='/pengajuan')

@pengajuan_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_tugas():
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        course_id = request.form.get('course')
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('file')

        if not all([course_id, title, file]):
            flash('Mata kuliah, judul, dan file tugas harus diisi.', 'error')
            return redirect(url_for('pengajuan.upload_tugas'))

        course = Course.query.get(course_id)
        if not course:
            flash('Mata kuliah tidak ditemukan.', 'error')
            return redirect(url_for('pengajuan.upload_tugas'))

        # Ensure the upload directory exists
        upload_folder = 'app/static/uploads/tugas'
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = f"{current_user.nim}_{course.kode}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        submission = Submission(
            student_id=current_user.id,
            course_id=course.id,
            judul=title,
            deskripsi=description,
            file_path=file_path,
            status='pending'
        )
        db.session.add(submission)
        db.session.commit()

        flash('Tugas berhasil diupload!', 'success')
        return redirect(url_for('pengajuan.status_pengajuan'))

    courses = Course.query.all()
    return render_template('pengajuan_upload.html', courses=courses)

@pengajuan_bp.route('/surat', methods=['GET', 'POST'])
@login_required
def ajukan_surat():
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        letter_type = request.form.get('letter_type')
        title = request.form.get('title')
        description = request.form.get('description')

        if not all([letter_type, title, description]):
            flash('Semua field harus diisi.', 'error')
            return redirect(url_for('pengajuan.ajukan_surat'))

        letter_submission = LetterSubmission(
            student_id=current_user.id,
            letter_type=letter_type,
            title=title,
            description=description,
            status='pending'
        )
        db.session.add(letter_submission)
        db.session.commit()

        flash('Pengajuan surat berhasil dikirim!', 'success')
        return redirect(url_for('pengajuan.status_pengajuan'))

    return render_template('pengajuan_surat.html')

@pengajuan_bp.route('/status')
@login_required
def status_pengajuan():
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))

    submissions = Submission.query.filter_by(student_id=current_user.id).order_by(Submission.submitted_at.desc()).all()
    letter_submissions = LetterSubmission.query.filter_by(student_id=current_user.id).order_by(LetterSubmission.submitted_at.desc()).all()
    internships = InternshipApplication.query.filter_by(student_id=current_user.id).order_by(InternshipApplication.submitted_at.desc()).all()
    theses = ThesisApplication.query.filter_by(student_id=current_user.id).order_by(ThesisApplication.submitted_at.desc()).all()

    return render_template('pengajuan_status.html', 
                         submissions=submissions, 
                         letter_submissions=letter_submissions,
                         internships=internships,
                         theses=theses)
@pengajuan_bp.route('/magang', methods=['GET', 'POST'])
@login_required
def magang():
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        perusahaan = request.form.get('perusahaan')
        posisi = request.form.get('posisi')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        reason = request.form.get('reason')
        file = request.files.get('file')

        file_path = None
        if file:
            upload_folder = 'app/static/uploads/magang'
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"magang_{current_user.nim}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

        new_app = InternshipApplication(
            student_id=current_user.id,
            perusahaan=perusahaan,
            posisi=posisi,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            file_path=file_path
        )
        db.session.add(new_app)
        db.session.commit()
        
        flash('Pengajuan magang berhasil dikirim!', 'success')
        return redirect(url_for('pengajuan.status_pengajuan'))
        
    return render_template('pengajuan_magang.html')

@pengajuan_bp.route('/skripsi', methods=['GET', 'POST'])
@login_required
def skripsi():
    if current_user.role != 'mahasiswa':
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        judul_skripsi = request.form.get('judul_skripsi')
        peminatan = request.form.get('peminatan')
        abstrak = request.form.get('abstrak')
        dosen_pref = request.form.get('dosen_pref')
        file = request.files.get('file')

        file_path = None
        if file:
            upload_folder = 'app/static/uploads/skripsi'
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"skripsi_{current_user.nim}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

        new_app = ThesisApplication(
            student_id=current_user.id,
            judul_skripsi=judul_skripsi,
            peminatan=peminatan,
            abstrak=abstrak,
            dosen_pref=dosen_pref,
            file_path=file_path
        )
        db.session.add(new_app)
        db.session.commit()
        
        flash('Pengajuan skripsi berhasil dikirim!', 'success')
        return redirect(url_for('pengajuan.status_pengajuan'))
        
    return render_template('pengajuan_skripsi.html')

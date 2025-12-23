from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app.models.user import User
from app.models.matkul import Course, Grade, Material, Video, Submission, KRS, LetterSubmission, Schedule
from app import db
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

akademik_bp = Blueprint('akademik', __name__, url_prefix='/akademik')

@akademik_bp.route('/krs')
@login_required
def krs():
    courses = Course.query.all()
    current_semester = 1
    current_tahun_ajaran = "2023/2024"
    krs_entries = KRS.query.filter_by(
        student_id=current_user.id,
        semester=current_semester,
        tahun_ajaran=current_tahun_ajaran
    ).all()
    selected_course_ids = [krs.course_id for krs in krs_entries]
    return render_template('akademik_krs.html',
                         courses=courses,
                         krs_entries=krs_entries,
                         selected_course_ids=selected_course_ids)

@akademik_bp.route('/krs/submit', methods=['POST'])
@login_required
def submit_krs():
    if current_user.role != 'mahasiswa':
        return jsonify({'status': 'error', 'message': 'Unauthorized'})

    data = request.get_json()
    selected_course_ids = data.get('course_ids', [])

    if not selected_course_ids:
        return jsonify({'status': 'error', 'message': 'Pilih minimal satu mata kuliah'})

    courses = Course.query.filter(Course.id.in_(selected_course_ids)).all()
    if len(courses) != len(selected_course_ids):
        return jsonify({'status': 'error', 'message': 'Beberapa mata kuliah tidak ditemukan'})

    current_semester = 1
    current_tahun_ajaran = "2023/2024"

    existing_krs = KRS.query.filter_by(
        student_id=current_user.id,
        semester=current_semester,
        tahun_ajaran=current_tahun_ajaran
    ).all()

    for krs_entry in existing_krs:
        db.session.delete(krs_entry)

    for course_id in selected_course_ids:
        krs_entry = KRS(
            student_id=current_user.id,
            course_id=course_id,
            semester=current_semester,
            tahun_ajaran=current_tahun_ajaran,
            status='pending'
        )
        db.session.add(krs_entry)

    db.session.commit()
    flash('KRS berhasil diajukan! Menunggu persetujuan dari akademik.', 'success')
    return jsonify({'status': 'success', 'message': 'KRS berhasil diajukan'})

@akademik_bp.route('/khs')
@login_required
def khs():
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    grades_by_semester = {}
    overall_total_bobot = 0
    overall_total_nilai_bobot = 0

    for grade in grades:
        semester = grade.semester
        if semester not in grades_by_semester:
            grades_by_semester[semester] = []
        grades_by_semester[semester].append(grade)

    semester_gpas = {}
    for semester, semester_grades in grades_by_semester.items():
        total_bobot = sum(grade.bobot for grade in semester_grades)
        total_nilai_bobot = sum(grade.nilai * grade.bobot for grade in semester_grades)
        semester_gpa = total_nilai_bobot / total_bobot if total_bobot > 0 else 0
        semester_gpas[semester] = round(semester_gpa, 2)
        overall_total_bobot += total_bobot
        overall_total_nilai_bobot += total_nilai_bobot

    overall_ipk = overall_total_nilai_bobot / overall_total_bobot if overall_total_bobot > 0 else 0
    return render_template('akademik_khs.html',
                         grades_by_semester=grades_by_semester,
                         semester_gpas=semester_gpas,
                         overall_ipk=round(overall_ipk, 2))

@akademik_bp.route('/khs/download')
@login_required
def download_khs_pdf():
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    grades_by_semester = {}
    for grade in grades:
        semester = grade.semester
        if semester not in grades_by_semester:
            grades_by_semester[semester] = []
        grades_by_semester[semester].append(grade)

    total_bobot = sum(grade.bobot for grade in grades)
    total_nilai_bobot = sum(grade.nilai * grade.bobot for grade in grades)
    overall_ipk = total_nilai_bobot / total_bobot if total_bobot > 0 else 0

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=20, alignment=1)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=14, spaceAfter=15, alignment=1)

    story = []
    story.append(Paragraph("Kartu Hasil Studi (KHS)", title_style))
    story.append(Paragraph("Semester 5 - Genap 2023/2024", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Nama: {current_user.nama}", styles['Normal']))
    story.append(Paragraph(f"NIM: {current_user.nim}", styles['Normal']))
    story.append(Paragraph(f"Program Studi: {current_user.program_studi}", styles['Normal']))
    story.append(Spacer(1, 12))

    current_semester_grades = grades_by_semester.get(5, [])
    if current_semester_grades:
        semester_total_bobot = sum(grade.bobot for grade in current_semester_grades)
        semester_total_nilai_bobot = sum(grade.nilai * grade.bobot for grade in current_semester_grades)
        semester_ip = semester_total_nilai_bobot / semester_total_bobot if semester_total_bobot > 0 else 0
    else:
        semester_ip = 0

    summary_data = [
        ['IP Semester', f'{semester_ip:.2f}', 'Sangat Memuaskan'],
        ['Total SKS', str(sum(grade.bobot for grade in current_semester_grades)) if current_semester_grades else '0', 'Semester Ini'],
        ['Mata Kuliah', str(len(current_semester_grades)) if current_semester_grades else '0', 'Lulus Semua'],
        ['IP Kumulatif', f'{overall_ipk:.2f}', 'Overall']
    ]

    summary_table = Table(summary_data, colWidths=[100, 80, 120])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    if current_semester_grades:
        story.append(Paragraph("Nilai Semester 5", styles['Heading3']))
        story.append(Spacer(1, 8))
        data = [['Kode', 'Mata Kuliah', 'SKS', 'Nilai', 'Bobot', 'Grade', 'Status']]
        for grade in current_semester_grades:
            data.append([
                grade.course.kode if grade.course else 'N/A',
                grade.course.nama if grade.course else 'N/A',
                str(grade.bobot),
                str(grade.nilai),
                f"{grade.nilai * grade.bobot:.2f}",
                grade.grade,
                'Lulus'
            ])
        table = Table(data, colWidths=[50, 150, 30, 40, 50, 40, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(table)

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'KHS_{current_user.nim}.pdf', mimetype='application/pdf')

@akademik_bp.route('/jadwal')
@login_required
def jadwal():
    schedule = Schedule.query.filter_by(semester=1).all()
    # Convert to list of dicts for template if needed, or update template to use objects
    return render_template('akademik_jadwal.html', schedule=schedule)

@akademik_bp.route('/nilai-keseluruhan')
@login_required
def nilai_keseluruhan():
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    total_sks = sum(grade.bobot for grade in grades)
    total_points = sum(grade.nilai * grade.bobot for grade in grades)
    ipk = total_points / total_sks if total_sks > 0 else 0
    return render_template('akademik_nilai_keseluruhan.html', grades=grades, ipk=round(ipk, 2), total_sks=total_sks)

@akademik_bp.route('/transkrip')
@login_required
def transkrip():
    grades = Grade.query.filter_by(student_id=current_user.id).order_by(Grade.semester).all()
    return render_template('akademik_transkrip.html', grades=grades)

@akademik_bp.route('/profil')
@login_required
def profil():
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    total_sks = sum(grade.bobot for grade in grades)
    total_points = sum(grade.nilai * grade.bobot for grade in grades)
    ipk = total_points / total_sks if total_sks > 0 else 0
    
    # academic history for timeline
    grades_by_semester = {}
    for grade in grades:
        sem = grade.semester
        if sem not in grades_by_semester:
            grades_by_semester[sem] = {'sks': 0, 'points': 0}
        grades_by_semester[sem]['sks'] += grade.bobot
        grades_by_semester[sem]['points'] += grade.nilai * grade.bobot
        
    history = []
    for sem in sorted(grades_by_semester.keys(), reverse=True):
        sem_data = grades_by_semester[sem]
        sem_ip = sem_data['points'] / sem_data['sks'] if sem_data['sks'] > 0 else 0
        history.append({
            'semester': sem,
            'sks': sem_data['sks'],
            'ip': round(sem_ip, 2)
        })
        
    return render_template('akademik_profil.html', 
                         ipk=round(ipk, 2), 
                         total_sks=total_sks,
                         history=history)

@akademik_bp.route('/profil/update', methods=['POST'])
@login_required
def update_profil():
    data = request.get_json()
    current_user.nama = data.get('nama', current_user.nama)
    current_user.email = data.get('email', current_user.email)
    current_user.program_studi = data.get('program_studi', current_user.program_studi)
    db.session.commit()
    flash('Profil berhasil diperbarui!', 'success')
    return jsonify({'status': 'success', 'message': 'Profil berhasil diperbarui'})

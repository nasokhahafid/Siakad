from flask import Blueprint, request, jsonify
from ..models.matkul import Course
from .. import db
from flask_login import login_required, current_user

matkul_bp = Blueprint('matkul', __name__)

@matkul_bp.route('/matakuliah', methods=['GET'])
@login_required
def get_courses():
    """Get all courses with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        semester = request.args.get('semester', type=int)

        query = Course.query

        if search:
            query = query.filter(
                (Course.nama.contains(search)) |
                (Course.kode.contains(search))
            )

        if semester:
            query = query.filter(Course.semester == semester)

        courses = query.paginate(page=page, per_page=per_page, error_out=False)

        result = {
            'status': 'success',
            'message': 'Courses retrieved successfully',
            'data': {
                'courses': [{
                    'id': course.id,
                    'kode': course.kode,
                    'nama': course.nama,
                    'sks': course.sks,
                    'semester': course.semester,
                    'dosen': {
                        'id': course.dosen.id,
                        'nama': course.dosen.nama,
                        'nim': course.dosen.nim
                    } if course.dosen else None
                } for course in courses.items],
                'pagination': {
                    'page': courses.page,
                    'per_page': courses.per_page,
                    'total': courses.total,
                    'pages': courses.pages,
                    'has_next': courses.has_next,
                    'has_prev': courses.has_prev
                }
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve courses: {str(e)}'
        }), 500

@matkul_bp.route('/matakuliah/<int:course_id>', methods=['GET'])
@login_required
def get_course(course_id):
    """Get a specific course by ID"""
    try:
        course = Course.query.get_or_404(course_id)

        return jsonify({
            'status': 'success',
            'message': 'Course retrieved successfully',
            'data': {
                'id': course.id,
                'kode': course.kode,
                'nama': course.nama,
                'sks': course.sks,
                'semester': course.semester,
                'dosen': {
                    'id': course.dosen.id,
                    'nama': course.dosen.nama,
                    'nim': course.dosen.nim
                } if course.dosen else None
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve course: {str(e)}'
        }), 500

@matkul_bp.route('/matakuliah', methods=['POST'])
@login_required
def create_course():
    """Create a new course"""
    try:
        if current_user.role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ['kode', 'nama', 'sks', 'semester', 'dosen_nim']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400

        # Check if course code already exists
        existing_course = Course.query.filter_by(kode=data['kode']).first()
        if existing_course:
            return jsonify({
                'status': 'error',
                'message': 'Course code already exists'
            }), 400

        # Find the lecturer
        from ..models.user import User
        dosen = User.query.filter_by(nim=data['dosen_nim'], role='dosen').first()
        if not dosen:
            return jsonify({
                'status': 'error',
                'message': 'Lecturer not found'
            }), 400

        # Create course
        course = Course(
            kode=data['kode'],
            nama=data['nama'],
            sks=int(data['sks']),
            semester=int(data['semester']),
            dosen_id=dosen.id
        )

        db.session.add(course)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Course created successfully',
            'data': {
                'id': course.id,
                'kode': course.kode,
                'nama': course.nama,
                'sks': course.sks,
                'semester': course.semester,
                'dosen': {
                    'id': dosen.id,
                    'nama': dosen.nama,
                    'nim': dosen.nim
                }
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to create course: {str(e)}'
        }), 500

@matkul_bp.route('/matakuliah/<int:course_id>', methods=['PUT'])
@login_required
def update_course(course_id):
    """Update a course"""
    try:
        if current_user.role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        course = Course.query.get_or_404(course_id)
        data = request.get_json()

        # Update fields
        if 'nama' in data:
            course.nama = data['nama']
        if 'sks' in data:
            course.sks = int(data['sks'])
        if 'semester' in data:
            course.semester = int(data['semester'])
        if 'dosen_nim' in data:
            from ..models.user import User
            dosen = User.query.filter_by(nim=data['dosen_nim'], role='dosen').first()
            if not dosen:
                return jsonify({
                    'status': 'error',
                    'message': 'Lecturer not found'
                }), 400
            course.dosen_id = dosen.id

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Course updated successfully',
            'data': {
                'id': course.id,
                'kode': course.kode,
                'nama': course.nama,
                'sks': course.sks,
                'semester': course.semester,
                'dosen': {
                    'id': course.dosen.id,
                    'nama': course.dosen.nama,
                    'nim': course.dosen.nim
                } if course.dosen else None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to update course: {str(e)}'
        }), 500

@matkul_bp.route('/matakuliah/<int:course_id>', methods=['DELETE'])
@login_required
def delete_course(course_id):
    """Delete a course"""
    try:
        if current_user.role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        course = Course.query.get_or_404(course_id)

        db.session.delete(course)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Course deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete course: {str(e)}'
        }), 500

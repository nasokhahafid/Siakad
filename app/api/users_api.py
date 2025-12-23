from flask import Blueprint, request, jsonify
from ..models.user import User
from .. import db, bcrypt
from flask_login import login_required, current_user
import re

users_bp = Blueprint('users', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_nim(nim):
    return len(nim) >= 5 and nim.isalnum()

@users_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """Get all users with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        role = request.args.get('role', '')

        query = User.query

        if search:
            query = query.filter(
                (User.nama.contains(search)) |
                (User.nim.contains(search)) |
                (User.email.contains(search))
            )

        if role:
            query = query.filter(User.role == role)

        users = query.paginate(page=page, per_page=per_page, error_out=False)

        result = {
            'status': 'success',
            'message': 'Users retrieved successfully',
            'data': {
                'users': [{
                    'id': user.id,
                    'nim': user.nim,
                    'nama': user.nama,
                    'email': user.email,
                    'program_studi': user.program_studi,
                    'role': user.role,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                } for user in users.items],
                'pagination': {
                    'page': users.page,
                    'per_page': users.per_page,
                    'total': users.total,
                    'pages': users.pages,
                    'has_next': users.has_next,
                    'has_prev': users.has_prev
                }
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve users: {str(e)}'
        }), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = User.query.get_or_404(user_id)

        return jsonify({
            'status': 'success',
            'message': 'User retrieved successfully',
            'data': {
                'id': user.id,
                'nim': user.nim,
                'nama': user.nama,
                'email': user.email,
                'program_studi': user.program_studi,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve user: {str(e)}'
        }), 500

@users_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    """Create a new user"""
    try:
        if current_user.role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ['nim', 'nama', 'email', 'program_studi', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400

        # Validate NIM format
        if not validate_nim(data['nim']):
            return jsonify({
                'status': 'error',
                'message': 'Invalid NIM format'
            }), 400

        # Validate email format
        if not validate_email(data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email format'
            }), 400

        # Check if NIM or email already exists
        existing_user = User.query.filter(
            (User.nim == data['nim']) | (User.email == data['email'])
        ).first()

        if existing_user:
            return jsonify({
                'status': 'error',
                'message': 'NIM or email already exists'
            }), 400

        # Validate role
        valid_roles = ['mahasiswa', 'dosen', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role'
            }), 400

        # Hash password
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Create user
        user = User(
            nim=data['nim'],
            nama=data['nama'],
            email=data['email'],
            program_studi=data['program_studi'],
            password=hashed_password,
            role=data['role']
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': {
                'id': user.id,
                'nim': user.nim,
                'nama': user.nama,
                'email': user.email,
                'program_studi': user.program_studi,
                'role': user.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to create user: {str(e)}'
        }), 500

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update a user"""
    try:
        if current_user.role != 'admin' and current_user.id != user_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # Update fields
        if 'nama' in data:
            user.nama = data['nama']
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid email format'
                }), 400
            # Check if email is already used by another user
            existing_user = User.query.filter(User.email == data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Email already exists'
                }), 400
            user.email = data['email']
        if 'program_studi' in data:
            user.program_studi = data['program_studi']
        if 'role' in data and current_user.role == 'admin':
            valid_roles = ['mahasiswa', 'dosen', 'admin']
            if data['role'] not in valid_roles:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid role'
                }), 400
            user.role = data['role']
        if 'password' in data and data['password']:
            user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'User updated successfully',
            'data': {
                'id': user.id,
                'nim': user.nim,
                'nama': user.nama,
                'email': user.email,
                'program_studi': user.program_studi,
                'role': user.role
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to update user: {str(e)}'
        }), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete a user"""
    try:
        if current_user.role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        user = User.query.get_or_404(user_id)

        # Prevent deleting admin users if there's only one admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify({
                    'status': 'error',
                    'message': 'Cannot delete the last admin user'
                }), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete user: {str(e)}'
        }), 500

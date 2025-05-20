import logging
import re
from config import settings, get_db_pool  # Menggunakan settings terpusat
import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from middlewares.auth import token_required
from services.user_service import UserService
from dao.user_dao import UserDAO

from utils.exceptions import (
    DatabaseError,
    DuplicateEntryError,
    RecordNotFoundError,
    InvalidDataError,
    TransactionError
)

user_bp = Blueprint('users', __name__)

async def get_service():
    pool = await get_db_pool()
    dao = UserDAO(pool)
    return UserService(dao)


# Helper Functions
def validate_username(username):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise InvalidDataError('username', username, '3-20 karakter (huruf, angka, underscore)')


def validate_password(password):
    if len(password) < 8:
        raise InvalidDataError('password', '****', 'minimal 8 karakter')
    if not any(c.isupper() for c in password):
        raise InvalidDataError('password', '****', 'minimal 1 huruf besar')
    if not any(c.isdigit() for c in password):
        raise InvalidDataError('password', '****', 'minimal 1 angka')




# Error Handlers
@user_bp.app_errorhandler(DatabaseError)
def handle_database_error(e):
    response = {
        'error': 'Database Error',
        'message': str(e),
        'code': e.__class__.__name__
    }

    if isinstance(e, DuplicateEntryError):
        response.update({
            'error': 'Conflict',
            'field': e.field,
            'status': 409
        })
        return jsonify(response), 409

    if isinstance(e, RecordNotFoundError):
        response.update({
            'error': 'Not Found',
            'model': e.model,
            'status': 404
        })
        return jsonify(response), 404

    if isinstance(e, InvalidDataError):
        response.update({
            'error': 'Invalid Input',
            'field': e.field,
            'requirement': e.requirement,
            'status': 400
        })
        return jsonify(response), 400

    response['status'] = 500
    return jsonify(response), 500


# Routes
@user_bp.route('/login', methods=['POST'])
async def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            raise InvalidDataError('credentials', None, 'username dan password diperlukan')

        service = await get_service()
        user = await service.dao.verify_password(data['username'], data['password'])

        if not user:
            raise InvalidDataError('credentials', None, 'kombinasi username/password salah')

        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=8)
        }
        token = jwt.encode(token_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        })

    except InvalidDataError as e:
        logging.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': 'Validation Error',
            'message': str(e),
            'field': e.field,
            'requirement': e.requirement
        }), 400

    except Exception as e:
        logging.error("Login error:", exc_info=True)  # <-- Tambahkan ini
        return jsonify({
            'error': 'Authentication Failed',
            'message': 'Proses autentikasi gagal',
            'internal_error': str(e)  # Hanya untuk development!
        }), 500

@user_bp.route('/me', methods=['GET'])
@token_required()
async def get_current_user():
    return jsonify({
        'id': request.user['id'],
        'username': request.user['username'],
        'role': request.user['role']
    })


@user_bp.route('/users', methods=['POST'])
@token_required(roles=['admin'])
async def create_user():
    try:
        data = request.get_json()
        if not data:
            raise InvalidDataError('payload', None, 'Data JSON diperlukan')

        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                raise InvalidDataError(field, None, 'Field ini diperlukan')

        validate_username(data['username'])
        validate_password(data['password'])

        role = data.get('role', 'user')
        if role not in ['user', 'admin']:
            raise InvalidDataError('role', role, 'Harus user atau admin')

        service = await get_service()
        user_id = await service.create_user(
            data['username'],
            data['password'],
            role
        )

        return jsonify({
            'id': user_id,
            'username': data['username'],
            'role': role
        }), 201

    except DatabaseError as e:
        raise e
    except Exception as e:
        raise DatabaseError(f'Gagal membuat user: {str(e)}')


@user_bp.route('/users', methods=['GET'])
@token_required(roles=['admin'])
async def get_all_users():
    try:
        service = await get_service()
        users = await service.get_all_users()
        return jsonify([{
            'id': u['id'],
            'username': u['username'],
            'role': u['role']
        } for u in users])
    except DatabaseError as e:
        raise e
    except Exception as e:
        raise DatabaseError(f'Gagal mengambil data user: {str(e)}')


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required()
async def get_user(user_id):
    try:
        service = await get_service()
        user = await service.dao.get_by_id(user_id)

        if not user:
            raise RecordNotFoundError('User', user_id)

        if request.user['role'] != 'admin' and request.user['id'] != user_id:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Akses ke resource ini ditolak'
            }), 403

        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        })
    except DatabaseError as e:
        raise e


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required(roles=['admin'])
async def update_user(user_id):
    try:
        if request.user['id'] == user_id:
            return jsonify({
                'error': 'Invalid Operation',
                'message': 'Tidak bisa mengupdate akun sendiri'
            }), 403

        data = request.get_json()
        if not data:
            raise InvalidDataError('payload', None, 'Data JSON diperlukan')

        required_fields = ['username', 'password', 'role']
        for field in required_fields:
            if field not in data:
                raise InvalidDataError(field, None, 'Field ini diperlukan')

        validate_username(data['username'])
        validate_password(data['password'])

        if data['role'] not in ['user', 'admin']:
            raise InvalidDataError('role', data['role'], 'Harus user atau admin')

        service = await get_service()
        updated = await service.update_user(
            user_id,
            data['username'],
            data['password'],
            data['role']
        )

        if not updated:
            raise DatabaseError('Gagal memperbarui user')

        return jsonify({
            'id': user_id,
            'username': data['username'],
            'role': data['role']
        })
    except DatabaseError as e:
        raise e


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required(roles=['admin'])
async def delete_user(user_id):
    try:
        if request.user['id'] == user_id:
            return jsonify({
                'error': 'Invalid Operation',
                'message': 'Tidak bisa menghapus akun sendiri'
            }), 403

        service = await get_service()
        deleted = await service.delete_user(user_id)

        if not deleted:
            raise RecordNotFoundError('User', user_id)

        return jsonify({
            'message': 'User berhasil dihapus',
            'user_id': user_id
        }), 200
    except DatabaseError as e:
        raise e


@user_bp.route('/users/search', methods=['GET'])
@token_required(roles=['admin'])
async def search_users():
    try:
        keyword = request.args.get('q', '').strip()
        if len(keyword) < 2:
            raise InvalidDataError('query', keyword, 'Minimal 2 karakter')

        service = await get_service()
        results = await service.search_users(keyword)

        return jsonify([{
            'id': u['id'],
            'username': u['username'],
            'role': u['role']
        } for u in results])
    except DatabaseError as e:
        raise e

@user_bp.route('/users/test-bcrypt', methods=['POST'])
async def test_bcrypt():
    data = request.get_json()
    password = data['password']
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    valid = bcrypt.checkpw(password.encode(), hashed.encode())
    return jsonify({
        "hashed": hashed,
        "valid": valid
    })
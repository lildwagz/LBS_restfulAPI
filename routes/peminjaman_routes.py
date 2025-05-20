from flask import Blueprint, request, jsonify
from config import get_db_pool
from middlewares.auth import token_required
from services.peminjaman_service import PeminjamanService
from dao.peminjaman_dao import PeminjamanDAO
from utils.exceptions import (
    DatabaseError,
    RecordNotFoundError,
    InvalidDataError,
    OperationNotAllowedError
)
import logging

peminjaman_bp = Blueprint('peminjaman', __name__)


async def get_service():
    pool = await get_db_pool()
    dao = PeminjamanDAO(pool)
    return PeminjamanService(dao)


def validate_peminjaman_data(data, is_admin=False):
    # Validasi data peminjaman
    required_fields = ['book_id']
    if not is_admin and 'user_id' in data:
        raise OperationNotAllowedError("User tidak boleh meminjam untuk user lain")

    if not all(field in data for field in required_fields):
        raise InvalidDataError('payload', None, 'Field book_id wajib diisi')


@peminjaman_bp.route('/peminjaman', methods=['POST'])
@token_required(roles=['user', 'admin'])
async def pinjam_buku():
    try:
        data = request.get_json()
        user = request.user
        service = await get_service()

        # Validasi input
        validate_peminjaman_data(data, is_admin=(user['role'] == 'admin'))

        user_id = data.get('user_id', user['id'])  # Admin bisa pinjam untuk user lain

        # Proses peminjaman
        peminjaman_id = await service.pinjam_buku(
            user_id=user_id,
            book_id=data['book_id']
        )

        return jsonify({
            "id": peminjaman_id,
            "message": "Peminjaman berhasil dibuat"
        }), 201

    except InvalidDataError as e:
        return jsonify({
            "error": "Validation Error",
            "field": e.field,
            "message": e.message
        }), 400
    except OperationNotAllowedError as e:
        return jsonify({
            "error": "Operation Not Allowed",
            "message": str(e)
        }), 403
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except DatabaseError as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            "error": "Database Error",
            "message": "Gagal memproses peminjaman"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


@peminjaman_bp.route('/peminjaman', methods=['GET'])
@token_required(roles=['admin'])
async def get_all_peminjaman():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        service = await get_service()
        result = await service.get_all_peminjaman(page, per_page)

        return jsonify({
            "data": result['data'],
            "pagination": result['pagination']
        })
    except InvalidDataError as e:
        return jsonify({
            "error": "Validation Error",
            "field": e.field,
            "message": e.message
        }), 400
    except DatabaseError as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            "error": "Database Error",
            "message": "Gagal mengambil data peminjaman"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


@peminjaman_bp.route('/peminjaman/<int:peminjaman_id>', methods=['GET'])
@token_required()
async def get_peminjaman(peminjaman_id):
    try:
        user = request.user
        service = await get_service()
        peminjaman = await service.get_peminjaman(peminjaman_id)

        # Authorization check
        if user['role'] != 'admin' and peminjaman['user_id'] != user['id']:
            raise OperationNotAllowedError("Akses ditolak untuk data ini")

        return jsonify(peminjaman)
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except OperationNotAllowedError as e:
        return jsonify({
            "error": "Forbidden",
            "message": str(e)
        }), 403
    except DatabaseError as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            "error": "Database Error",
            "message": "Gagal mengambil data peminjaman"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


@peminjaman_bp.route('/peminjaman/<int:peminjaman_id>/kembalikan', methods=['POST'])
@token_required()
async def kembalikan_buku(peminjaman_id):
    try:
        user = request.user
        service = await get_service()

        # Authorization check
        if user['role'] != 'admin':
            peminjaman = await service.get_peminjaman(peminjaman_id)
            if peminjaman['user_id'] != user['id']:
                raise OperationNotAllowedError("Hanya bisa mengembalikan buku sendiri")

        await service.kembalikan_buku(peminjaman_id)
        return jsonify({
            "message": "Buku berhasil dikembalikan",
            "peminjaman_id": peminjaman_id
        }), 200
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except OperationNotAllowedError as e:
        return jsonify({
            "error": "Forbidden",
            "message": str(e)
        }), 403
    except DatabaseError as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            "error": "Database Error",
            "message": "Gagal mengembalikan buku"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


@peminjaman_bp.route('/users/<int:user_id>/peminjaman', methods=['GET'])
@token_required()
async def get_user_peminjaman(user_id):
    try:
        user = request.user
        if user['role'] != 'admin' and user['id'] != user_id:
            raise OperationNotAllowedError("Akses ditolak untuk data user lain")

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        service = await get_service()
        result = await service.get_user_peminjaman(user_id, page, per_page)

        return jsonify({
            "data": result['data'],
            "pagination": result['pagination']
        })
    except OperationNotAllowedError as e:
        return jsonify({
            "error": "Forbidden",
            "message": str(e)
        }), 403
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except DatabaseError as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            "error": "Database Error",
            "message": "Gagal mengambil data peminjaman"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


# Error Handlers
@peminjaman_bp.errorhandler(InvalidDataError)
def handle_invalid_data_error(e):
    return jsonify({
        "error": "Validation Error",
        "field": e.field,
        "message": e.message
    }), 400


@peminjaman_bp.errorhandler(OperationNotAllowedError)
def handle_operation_error(e):
    return jsonify({
        "error": "Operation Not Allowed",
        "message": str(e)
    }), 403


@peminjaman_bp.errorhandler(RecordNotFoundError)
def handle_not_found_error(e):
    return jsonify({
        "error": "Not Found",
        "message": str(e)
    }), 404


@peminjaman_bp.errorhandler(500)
def handle_generic_error(e):
    return jsonify({
        "error": "Server Error",
        "message": "Terjadi kesalahan internal"
    }), 500
from flask import Blueprint, request, jsonify
from datetime import datetime
from config import get_db_pool
from dao.book_dao import BookDAO
from middlewares.auth import token_required
from services.book_services import BookService
from utils.exceptions import (
    DatabaseError,
    RecordNotFoundError,
    DuplicateEntryError,
    InvalidDataError
)
import logging

book_bp = Blueprint('books', __name__)


async def _get_service():
    pool = await get_db_pool()
    dao = BookDAO(pool)
    return BookService(dao)


def validate_book_data(data, is_update=False):
    # Validasi dasar untuk payload buku
    if not is_update and not all(field in data for field in ['judul', 'pengarang', 'stok', 'tahun_terbit']):
        raise InvalidDataError('payload', None, 'Semua field wajib diisi')

    if 'judul' in data:
        if len(data['judul']) < 2 or len(data['judul']) > 200:
            raise InvalidDataError('judul', data['judul'], '2-200 karakter')

    if 'stok' in data:
        if not isinstance(data['stok'], int) or data['stok'] < 0:
            raise InvalidDataError('stok', data['stok'], 'Harus bilangan bulat positif')

    if 'tahun_terbit' in data:
        current_year = datetime.now().year
        if not (1900 < data['tahun_terbit'] <= current_year + 1):
            raise InvalidDataError('tahun_terbit', data['tahun_terbit'],
                                   f'Tahun antara 1900-{current_year + 1}')


@book_bp.route('/books', methods=['GET'])
async def get_books():
    # try:
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    service = await _get_service()
    books = await service.get_all_books(page, per_page)
    return jsonify({
        "data": books,
        "meta": {
            "page": page,
            "per_page": per_page
        }
    }),200
    # except DatabaseError as e:
    #     logging.error(f"Database error: {str(e)}")
    #     return jsonify({
    #         "error": "Database Error",
    #         "message": "Gagal mengambil data buku"
    #     }), 500
    # except Exception as e:
    #     logging.error(f"Unexpected error: {str(e)}")
    #     return jsonify({
    #         "error": "Server Error",
    #         "message": "Terjadi kesalahan internal"
    #     }), 500


@book_bp.route('/books/<int:book_id>', methods=['GET'])
async def get_book(book_id):
    try:
        service = await _get_service()
        book = await service.get_book_by_id(book_id)
        return jsonify(book)
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except DatabaseError as e:
        return jsonify({
            "error": "Database Error",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


@book_bp.route('/books', methods=['POST'])
@token_required(roles=['admin'])
async def create_book():
    try:
        data = request.get_json()
        validate_book_data(data)

        service = await _get_service()
        book_id = await service.add_book(
            data['judul'],
            data['pengarang'],
            data['stok'],
            data['tahun_terbit']
        )

        return jsonify({
            "id": book_id,
            "message": "Buku berhasil ditambahkan"
        }), 201

    except DuplicateEntryError as e:
        return jsonify({
            "error": "Duplicate Entry",
            "field": e.field,
            "message": "Buku dengan judul ini sudah ada"
        }), 409
    except InvalidDataError as e:
        return jsonify({
            "error": "Validation Error",
            "field": e.field,
            "message": e.message
        }), 400
    except DatabaseError as e:
        return jsonify({
            "error": "Database Error",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": "Gagal menambahkan buku"
        }), 500


@book_bp.route('/books/<int:book_id>', methods=['PUT'])
@token_required(roles=['admin'])
async def update_book(book_id):
    try:
        data = request.get_json()
        validate_book_data(data, is_update=True)

        service = await _get_service()
        updated = await service.update_book(book_id, **data)

        return jsonify({
            "message": "Buku berhasil diperbarui",
            "book_id": book_id
        }), 200

    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except DuplicateEntryError as e:
        return jsonify({
            "error": "Duplicate Entry",
            "field": e.field,
            "message": "Buku dengan judul ini sudah ada"
        }), 409
    except InvalidDataError as e:
        return jsonify({
            "error": "Validation Error",
            "field": e.field,
            "message": e.message
        }), 400
    except DatabaseError as e:
        return jsonify({
            "error": "Database Error",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": "Gagal memperbarui buku"
        }), 500


@book_bp.route('/books/<int:book_id>', methods=['DELETE'])
@token_required(roles=['admin'])
async def delete_book(book_id):
    try:
        service = await _get_service()
        await service.delete_book(book_id)

        return jsonify({
            "message": "Buku berhasil dihapus",
            "book_id": book_id
        }), 200

    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except DatabaseError as e:
        return jsonify({
            "error": "Database Error",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": "Gagal menghapus buku"
        }), 500


@book_bp.route('/books/search', methods=['GET'])
async def search_books():
    try:
        keyword = request.args.get('q', '').strip()
        if len(keyword) < 2:
            raise InvalidDataError('query', keyword, 'Minimal 2 karakter')

        service = await _get_service()
        results = await service.search_books(keyword)

        return jsonify({
            "data": results,
            "meta": {
                "search_term": keyword,
                "result_count": len(results)
            }
        })
    except InvalidDataError as e:
        return jsonify({
            "error": "Validation Error",
            "field": e.field,
            "message": e.message
        }), 400
    except DatabaseError as e:
        return jsonify({
            "error": "Database Error",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": "Gagal melakukan pencarian"
        }), 500


@book_bp.route('/books/<int:book_id>/stock', methods=['PATCH'])
@token_required(roles=['admin'])
async def adjust_stock(book_id):
    try:
        data = request.get_json()
        if 'quantity' not in data or not isinstance(data['quantity'], int):
            raise InvalidDataError('quantity', None, 'Harus bilangan bulat')

        service = await _get_service()
        await service.adjust_stock(book_id, data['quantity'])

        return jsonify({
            "message": "Stok berhasil diupdate",
            "book_id": book_id,
            "new_quantity": data['quantity']
        }), 200

    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except InvalidDataError as e:
        return jsonify({
            "error": "Validation Error",
            "field": e.field,
            "message": e.message
        }), 400
    except DatabaseError as e:
        return jsonify({
            "error": "Database Error",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": "Gagal mengupdate stok"
        }), 500


# Error Handlers
@book_bp.errorhandler(InvalidDataError)
def handle_invalid_data_error(e):
    return jsonify({
        "error": "Validation Error",
        "field": e.field,
        "message": e.message
    }), 400


@book_bp.errorhandler(RecordNotFoundError)
def handle_not_found_error(e):
    return jsonify({
        "error": "Not Found",
        "message": str(e)
    }), 404


@book_bp.errorhandler(DuplicateEntryError)
def handle_duplicate_error(e):
    return jsonify({
        "error": "Duplicate Entry",
        "field": e.field,
        "message": "Data sudah ada di sistem"
    }), 409


@book_bp.errorhandler(500)
def handle_generic_error(e):
    return jsonify({
        "error": "Server Error",
        "message": "Terjadi kesalahan internal"
    }), 500
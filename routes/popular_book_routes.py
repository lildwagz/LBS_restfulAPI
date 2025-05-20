from flask import Blueprint, request, jsonify
from datetime import datetime
from config import get_db_pool
from middlewares.auth import token_required
from services.popular_book_service import PopularBookService
from dao.popular_book_dao import PopularBookDAO
from utils.exceptions import DatabaseError, InvalidDataError
import logging

popular_book_bp = Blueprint('popular_books', __name__)


async def get_service():
    pool = await get_db_pool()
    dao = PopularBookDAO(pool)
    return PopularBookService(dao)


@popular_book_bp.route('/analytics/popular-books', methods=['GET'])
@token_required(roles=['admin'])
async def get_popular_books():
    try:
        year = request.args.get('year', type=int)
        limit = request.args.get('limit', default=10, type=int)

        # Default ke tahun saat ini jika tidak ada input
        if not year:
            year = datetime.now().year

        service = await get_service()
        books = await service.get_popular_books(year, limit)

        return jsonify({
            "meta": {
                "year": year,
                "limit": limit,
                "count": len(books)
            },
            "data": books
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
            "message": "Gagal mengambil data buku populer"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


@popular_book_bp.route('/analytics/available-years', methods=['GET'])
@token_required(roles=['admin'])
async def get_available_years():
    try:
        service = await get_service()
        years = await service.get_available_years()
        return jsonify({
            "data": years,
            "count": len(years)
        })
    except DatabaseError as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({
            "error": "Database Error",
            "message": "Gagal mendapatkan tahun tersedia"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


# Error Handlers
@popular_book_bp.errorhandler(InvalidDataError)
def handle_invalid_data_error(e):
    return jsonify({
        "error": "Validation Error",
        "field": e.field,
        "message": e.message
    }), 400


@popular_book_bp.errorhandler(500)
def handle_generic_error(e):
    return jsonify({
        "error": "Server Error",
        "message": "Terjadi kesalahan internal"
    }), 500
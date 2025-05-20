from datetime import date
from flask import Blueprint, request, jsonify
from config import get_db_pool
from middlewares.auth import token_required
from services.report_service import ReportService
from dao.report_dao import ReportDAO
from utils.exceptions import DatabaseError, InvalidDataError
import logging

report_bp = Blueprint('reports', __name__)


async def get_service():
    pool = await get_db_pool()
    dao = ReportDAO(pool)
    return ReportService(dao)


def validate_date(date_str):
    """Validasi format tanggal ISO (YYYY-MM-DD)"""
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise InvalidDataError('date', date_str, 'Format tanggal tidak valid (YYYY-MM-DD)')


@report_bp.route('/reports', methods=['GET'])
@token_required(roles=['admin'])
async def get_report():
    try:
        filters = {
            "start_date": request.args.get('start_date'),
            "end_date": request.args.get('end_date'),
            "status": request.args.get('status'),
            "book_title": request.args.get('book_title'),
            "username": request.args.get('username')
        }

        # Validasi dan konversi tanggal
        date_errors = []
        for date_field in ['start_date', 'end_date']:
            if filters[date_field]:
                try:
                    filters[date_field] = validate_date(filters[date_field])
                except InvalidDataError as e:
                    date_errors.append(str(e))

        if date_errors:
            return jsonify({
                "error": "Validation Error",
                "messages": date_errors
            }), 400

        # Validasi status
        if filters['status'] and filters['status'] not in ['dipinjam', 'dikembalikan']:
            return jsonify({
                "error": "Validation Error",
                "field": "status",
                "message": "Status harus 'dipinjam' atau 'dikembalikan'"
            }), 400

        service = await get_service()
        report = await service.generate_report(**filters)

        return jsonify({
            "data": report,
            "meta": {
                "filter": filters,
                "count": len(report)
            }
        })

    except InvalidDataError as e:
        return jsonify({
            "error": "Validation Error",
            "field": e.field,
            "message": e.message
        }), 400
    except DatabaseError as e:
        logging.error(f"Report generation failed: {str(e)}")
        return jsonify({
            "error": "Report Error",
            "message": "Gagal menghasilkan laporan"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


@report_bp.route('/reports/filter-options', methods=['GET'])
@token_required(roles=['admin'])
async def get_filter_options():
    try:
        service = await get_service()
        options = await service.get_filter_options()
        return jsonify(options)
    except DatabaseError as e:
        logging.error(f"Filter options error: {str(e)}")
        return jsonify({
            "error": "Database Error",
            "message": "Gagal mengambil opsi filter"
        }), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Server Error",
            "message": "Terjadi kesalahan internal"
        }), 500


# Error Handlers
@report_bp.errorhandler(InvalidDataError)
def handle_invalid_data_error(e):
    return jsonify({
        "error": "Validation Error",
        "field": e.field,
        "message": e.message
    }), 400


@report_bp.errorhandler(500)
def handle_generic_error(e):
    return jsonify({
        "error": "Server Error",
        "message": "Terjadi kesalahan internal"
    }), 500
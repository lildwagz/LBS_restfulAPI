from flask import request, jsonify
import jwt
from functools import wraps
from config import settings  # Menggunakan settings terpusat
from jwt import PyJWTError


def token_required(roles=None):
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            # Ambil token dari header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "Authorization header tidak valid"}), 401

            try:
                # Ekstrak dan decode token
                token = auth_header.split()[1]
                payload = jwt.decode(
                    token,
                    settings.jwt.secret,  # Menggunakan konfigurasi terpusat
                    algorithms=[settings.jwt.algorithm],
                    issuer=settings.jwt.issuer,
                    options={
                        'require_exp': True,
                        'require_iat': True,
                        'verify_signature': True
                    }
                )

                # Cek role
                if roles and payload.get('role') not in roles:
                    return jsonify({"error": "Akses ditolak"}), 403

                # Simpan payload di context request
                request.user = payload

            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token kadaluarsa"}), 401
            except jwt.InvalidIssuerError:
                return jsonify({"error": "Issuer token tidak valid"}), 401
            except PyJWTError as e:
                return jsonify({"error": f"Error validasi token: {str(e)}"}), 401
            except Exception as e:
                return jsonify({"error": "Error internal server"}), 500

            return await f(*args, **kwargs)

        return wrapped

    return decorator
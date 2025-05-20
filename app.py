from flask import Flask, jsonify
from asgiref.wsgi import WsgiToAsgi
import os
import logging
from logging.handlers import RotatingFileHandler

from config import settings


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.update(
        SECRET_KEY=settings.jwt.secret,
        ENV=settings.app.env,
        DEBUG=os.getenv('DEBUG', 'false').lower() == 'true'
    )

    # Production Logging
    if app.config['ENV'] == 'production':
        file_handler = RotatingFileHandler(
            'app.log',
            maxBytes=1024 * 1024 * 10,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    # Blueprints
    from routes.book_routes import book_bp
    from routes.peminjaman_routes import peminjaman_bp
    from routes.user_routes import user_bp
    app.register_blueprint(book_bp)
    app.register_blueprint(peminjaman_bp)
    app.register_blueprint(user_bp)

    # Health Check
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'environment': app.config['ENV']}), 200

    return app


app = create_app()
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', '5000'))
    )
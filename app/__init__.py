import logging
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from config import Config

db = SQLAlchemy()

# Dodaj tutaj nową funkcję (lub w środku create_app)
def fix_url_filter(url):
    """Filtr poprawiający URL"""
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        return f"http://{url}"
    return url

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Zarejestruj filtr w środowisku Jinja2
    app.jinja_env.filters['fix_url'] = fix_url_filter  # <--- TUTAJ

    db.init_app(app)

    # Globalna obsługa błędów
    @app.errorhandler(OperationalError)
    def handle_database_error(e):
        app.logger.error(f"""
            🚨 BŁĄD BAZY DANYCH 🚨
            Ścieżka: {request.path}
            Błąd: {str(e)}
        """)
        db.session.remove()
        return render_template('database_error.html'), 500

    from app.routes import main
    app.register_blueprint(main)

    return app
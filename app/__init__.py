import logging
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)

    # Globalna obsługa błędów dla WSZYSTKICH endpointów
    @app.errorhandler(OperationalError)
    def handle_database_error(e):
        app.logger.error(f"""
            🚨 BŁĄD BAZY DANYCH 🚨
            Ścieżka: {request.path}
            Błąd: {str(e)}
        """)
        db.session.remove()  # Czyści uszkodzone sesje
        return render_template('database_error.html'), 500
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app


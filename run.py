import app
from app import create_app, db

flask_app = create_app()

if __name__ == '__main__':
    with flask_app.app_context():
        # Registers all models with SQLAlchemy
        import app.models
    flask_app.run(host='0.0.0.0',debug=True, port=8080)
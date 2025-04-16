import app
print(app.__file__)

from app import create_app, db

flask_app = create_app()

if __name__ == '__main__':
    with flask_app.app_context():
        # Registers all models with SQLAlchemy
        import app.models
    flask_app.run(debug=True)
from dotenv import load_dotenv # Dodaj tę linię

import app
from app import create_app, db
load_dotenv() # Dodaj tę linię

flask_app = create_app()

if __name__ == '__main__':
    with flask_app.app_context():
        # Registers all models with SQLAlchemy
        import app.models
    flask_app.run(host='0.0.0.0', port=8080)
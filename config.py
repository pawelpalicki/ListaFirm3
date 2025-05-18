import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-should-be-changed'
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://')
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///firmy.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
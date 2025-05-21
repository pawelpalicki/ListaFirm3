import os
# from dotenv import load_dotenv 
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv() 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jakis_domyslny_klucz_na_wypadek_braku_env'
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://')
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///firmy.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'max_overflow': 20
    }
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'instance')
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(INSTANCE_PATH, 'pkm_sdit.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
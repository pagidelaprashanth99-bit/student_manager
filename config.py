import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Use environment variable for SECRET_KEY in production, fallback to default for development
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret123-change-in-production')
    
    # Use environment variable for database URI (for PostgreSQL in production)
    # Fallback to SQLite for local development
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Handle PostgreSQL URL format (some platforms add postgres://, need postgresql://)
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

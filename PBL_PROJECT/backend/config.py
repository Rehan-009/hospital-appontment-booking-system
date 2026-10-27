import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hospital_appointment_system_secure_secret_key_2026')
    
    # MySQL Database Configuration
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'hospital_db')
    
    # SQLite Fallback Path
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SQLITE_PATH = os.path.join(BASE_DIR, 'database', 'hospital.db')
    
    # Session Configuration
    SESSION_COOKIE_NAME = 'habs_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

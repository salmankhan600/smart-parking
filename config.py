import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'smart-parking-secret-key-production-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # DB configuration with SQLite default fallback & MySQL support
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()
    
    if DB_TYPE == 'mysql':
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME', 'smart_parking_db')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        db_file = os.getenv('DATABASE_FILE', 'smart_parking.db')
        base_dir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(base_dir, db_file)}"

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = BASE_DIR

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-only-change-this-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    ITEMS_PER_PAGE = 9

    @staticmethod
    def get_database_uri():
        """
        Builds the SQLAlchemy Database URI.
        Supports explicit DATABASE_URL (MySQL or SQLite) or constructs
        a MySQL connection URI from discrete environment variables.
        Falls back to local SQLite if MySQL variables are not configured.
        """
        explicit_url = os.getenv('DATABASE_URL')
        if explicit_url:
            if explicit_url.startswith("postgres://"):
                explicit_url = explicit_url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif explicit_url.startswith("postgresql://") and "+psycopg2" not in explicit_url:
                explicit_url = explicit_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return explicit_url

        mysql_user = os.getenv('MYSQL_USER')
        mysql_host = os.getenv('MYSQL_HOST', 'localhost')
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        mysql_db = os.getenv('MYSQL_DATABASE', 'eduverse_ai')
        mysql_pwd = os.getenv('MYSQL_PASSWORD', '')

        if mysql_user and mysql_db:
            pwd_part = f":{mysql_pwd}" if mysql_pwd else ""
            return f"mysql+pymysql://{mysql_user}{pwd_part}@{mysql_host}:{mysql_port}/{mysql_db}"

        # Default fallback: check instance directory first, then project root
        instance_db = BASE_DIR / 'instance' / 'eduverse_dev.db'
        if instance_db.exists():
            return f"sqlite:///{instance_db}"

        # If running as packaged executable, copy bundled default DB to local instance/ folder
        if getattr(sys, 'frozen', False):
            bundled_db = BUNDLE_DIR / 'instance' / 'eduverse_dev.db'
            if bundled_db.exists():
                import shutil
                instance_dir = BASE_DIR / 'instance'
                instance_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(bundled_db, instance_db)
                return f"sqlite:///{instance_db}"

        if (BASE_DIR / 'eduverse_dev.db').exists():
            return f"sqlite:///{BASE_DIR / 'eduverse_dev.db'}"
        return f"sqlite:///{instance_db}"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    # Use dedicated SQLite test database for pytest
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

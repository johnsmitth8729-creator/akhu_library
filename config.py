import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def env_bool(name, default=False):
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    IS_PRODUCTION = os.environ.get("FLASK_ENV", "").lower() == "production"
    DEBUG = env_bool("FLASK_DEBUG", False)
    TIMEZONE_OFFSET = 5
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-please")
    # Default to a local PostgreSQL if not specified
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/alkhwarizmi")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    ALLOWED_PDF_EXTENSIONS = {"pdf"}
    ITEMS_PER_PAGE = 12
    DEFAULT_BORROW_DAYS = 14


    # =====================================================
    # MAIL CONFIGURATION
    # =====================================================

    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.environ.get(
            "MAIL_PORT",
            587
        )
    )

    MAIL_USE_TLS = True

    MAIL_USE_SSL = False

    MAIL_USERNAME = os.environ.get(
        "MAIL_USERNAME"
    )

    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD"
    )

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "Al-Khwarizmi Smart Library"
    )


    # =====================================================
    # SECURITY
    # =====================================================

    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", IS_PRODUCTION)

    REMEMBER_COOKIE_SECURE = env_bool("REMEMBER_COOKIE_SECURE", SESSION_COOKIE_SECURE)

    SESSION_COOKIE_HTTPONLY = True

    REMEMBER_COOKIE_HTTPONLY = True

    PERMANENT_SESSION_LIFETIME = 3600

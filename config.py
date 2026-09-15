import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # No fallback: fail loudly at startup instead of silently running with a
    # guessable, committed-to-git secret key.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Set it in your local .env and in Render's environment settings."
        )

    # Uses Render's managed Postgres (DATABASE_URL) when present, falls back
    # to local SQLite for development. Render/Heroku-style URLs start with
    # 'postgres://', which SQLAlchemy 2.x rejects — normalize to 'postgresql://'.
    _db_url = os.environ.get("DATABASE_URL")
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url or (
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "3moc.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie hardening
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") != "development"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
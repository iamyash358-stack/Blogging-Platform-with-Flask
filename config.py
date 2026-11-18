import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


def _db_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        return "sqlite:///" + os.path.join(basedir, "instance", "blog.db")
    # Heroku/Render style URLs
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 6
    COMMENTS_MAX_LENGTH = 1000
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    POSTS_PER_PAGE = 5

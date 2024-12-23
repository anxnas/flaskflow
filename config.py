import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")

    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://testuser:testpassword@db:5432/testdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery + Redis
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_ALGORITHM = "HS256"

    # Автообновление
    AUTO_REFRESH_OPTIONS = {
        "0": "0 сек",
        "10": "10 сек",
        "15": "15 сек",
        "30": "30 сек",
        "60": "1 минута"
    }

    # Логирование
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

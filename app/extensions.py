from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from celery import Celery
from loguru import logger
from flask import Flask
from datetime import timedelta
import jwt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def make_celery() -> Celery:
    return Celery(__name__)

celery = make_celery()

class SimpleJWT:
    def init_app(self, app: Flask) -> None:
        self.secret_key = app.config["JWT_SECRET_KEY"]
        self.algorithm = app.config["JWT_ALGORITHM"]
        self.expires_in = timedelta(hours=1)

jwt = SimpleJWT()

logger.add("stderr", level="INFO")

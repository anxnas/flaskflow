from flask import Flask, redirect, url_for
from .extensions import db, migrate, login_manager, celery, jwt, logger
from config import Config
from .admin import admin_bp
from api import api_bp
from user_area import user_bp
from cli import cli_bp

def create_app(config_class=Config) -> Flask:
    """Flask приложение"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "admin_bp.admin_login"

    celery.conf.update(app.config)

    jwt.init_app(app)

    logger.info("Приложение запускается")

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(cli_bp)

    @app.route("/")
    def index():
        return redirect(url_for("admin_bp.admin_login"))

    return app

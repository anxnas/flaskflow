from flask import Blueprint

user_bp = Blueprint("user_bp", __name__, template_folder="templates")

from . import routes

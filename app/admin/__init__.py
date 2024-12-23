from flask import Blueprint

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates")

from . import routes

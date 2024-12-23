from flask import Blueprint

cli_bp = Blueprint("cli_bp", __name__)

from . import commands

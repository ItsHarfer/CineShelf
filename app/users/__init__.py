from flask import Blueprint

users_bp = Blueprint("users", __name__, template_folder="templates")

from app.users import routes

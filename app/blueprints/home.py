# app/blueprints/home.py

import logging
from flask import Blueprint, render_template, request

from app.models import db
from app.data_manager import DataManager
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

home_bp = Blueprint("home", __name__)


@home_bp.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@home_bp.route("/")
def home():
    try:

        user_id = request.args.get("user_id", type=int)
        message = request.args.get("message")

        users = DataManager(db).get_users()

        if not user_id and users:
            user_id = users[0].id

        selected_user = next((u for u in users if u.id == user_id), None)

        movies = selected_user.movies.all() if selected_user else []

        return render_template(
            "index.html",
            users=users,
            selected_user=selected_user,
            selected_user_id=user_id,
            movies=movies,
            message=message,
        )
    except SQLAlchemyError:
        logger.exception("Database error during home rendering")
        raise
    except Exception:
        logger.exception("Unexpected error in home()")
        raise

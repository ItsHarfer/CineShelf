# app/blueprints/home.py

import logging
from flask import Blueprint, render_template, request

from app import db
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
        message = request.args.get("message")

        # users ist jetzt eine Liste, weil get_users() .all() aufruft
        users = DataManager(db).get_users()

        # 1) gewählte user_id aus Query-String
        user_id = request.args.get("user_id", type=int)
        # 2) falls noch keine da ist, nimm den ersten User
        if not user_id and users:
            user_id = users[0].id

        # ausgewählten User finden
        selected_user = next((u for u in users if u.id == user_id), None)

        # movies-Query ausführen, da lazy="dynamic"
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

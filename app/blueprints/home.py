# File: app/blueprints/home.py
"""
Purpose:
    Render the home page with user selection and associated movies, handling potential errors gracefully.

Features:
    - Fetch all users from the database
    - Default to the first user if none is selected
    - Retrieve movies for the selected user
    - Render the index.html template with context

Exceptions:
    - SQLAlchemyError: raised when database operations fail
    - Exception: raised on unexpected errors

Author: Martin Haferanke
Date: 2025-07-18

"""
import logging
from typing import List, Optional

from flask import Blueprint, render_template, request, abort
from sqlalchemy.exc import SQLAlchemyError

from app.models import db
from app.services.data_manager import DataManager

logger = logging.getLogger(__name__)

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home() -> str:
    """
    Render the home view displaying users and their movies.

    :return: Rendered HTML for the home page
    :raises SQLAlchemyError: when database queries fail
    :raises Exception: on unexpected errors
    """
    try:
        # Parse query parameters
        user_id: Optional[int] = request.args.get("user_id", type=int)
        message: Optional[str] = request.args.get("message")

        # Retrieve all users
        users: List = DataManager(db).get_users()

        # Default to first user if none selected and users exist
        if user_id is None and users:
            user_id = users[0].id  # type: ignore

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
        abort(500)
    except Exception:
        logger.exception("Unexpected error in home()")
        abort(500)

# File: app/blueprints/users.py
"""
Purpose:
    Handles user and movie management routes including creation, deletion, viewing, and error
    handling for HTTP and application-specific errors.

Features:
    - User creation and deletion
    - Searching and adding movies via OMDB API
    - Editing and updating movie details
    - Blueprint-specific HTTP error handlers for 404 and 500

Exceptions:
    - ValueError: raised when converting year to int fails
    - TypeError: raised when slicing non-string year input
    - SQLAlchemyError: database transaction failures
    - JSONDecodeError: OMDB fetch data parsing errors

Author: Martin Haferanke
Date: 2025-07-18
"""
import logging
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, abort
from sqlalchemy.exc import SQLAlchemyError

from app import limiter
from app.services.data_manager import DataManager
from app.models import User, Movie, db
from app.utils import fetch_omdb_data

users_bp = Blueprint("users", __name__, url_prefix="/users")
data_manager = DataManager(db)


@users_bp.route("/add", methods=["GET", "POST"])
def add_user():
    """
    Create a new user.

    GET: render user creation form.
    POST: process form, create user, and redirect home.

    :return: Redirect URL or rendered template
    :raises ValueError: if username is invalid
    :raises SQLAlchemyError: if database operation fails
    """
    if request.method == "POST":
        username: str = request.form.get("username", "").strip()
        if not username:
            raise ValueError("Username cannot be empty")
        user = data_manager.create_user(username)
        message = f'User "{user.name}" successfully created.'
        return redirect(url_for("home.home", user_id=user.id, message=message))

    # GET
    return render_template("users/add.html")


@users_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id: int):
    """
    Delete an existing user.

    :param user_id: ID of the user to delete
    :return: Redirect URL to home with status message
    :raises SQLAlchemyError: if deletion fails
    """
    user = User.query.get_or_404(user_id)
    data_manager.delete_user(user_id)
    message = f'User "{user.name}" deleted.'

    return redirect(url_for("home.home", message=message))


@limiter.limit("10/minute")
@users_bp.route("/<int:user_id>/movies", methods=["GET", "POST"])
def user_movies(user_id: int):
    """
    View and manage movies for a user (Rate-limited).
    This endpoint is limited to 10 requests per minute
    per user to prevent abuse.

    GET with modal parameter: search or add movie form.
    POST: add movie to user's favourites.

    :param user_id: ID of the user
    :return: Redirect URL or rendered template
    """
    user = User.query.get_or_404(user_id)

    # GET
    if request.method == "GET" and request.args.get("modal"):
        title: str = request.args.get("title", "").strip()
        data: dict = {}

        if title:
            data = fetch_omdb_data(title)

        # Flag, if the search already performed
        search_performed: bool = bool(title)

        # Check if the movie is already in the favourites
        already_added: bool = False
        if data.get("Title"):
            exists = Movie.query.filter_by(user_id=user_id, name=data["Title"]).first()
            already_added = bool(exists)

        return render_template(
            "movies/add.html",
            user=user,
            data=data,
            already_added=already_added,
            search_performed=search_performed,
            message=request.args.get("message"),
        )

    # POST
    if request.method == "POST":
        title: str = request.form.get("title", "Unknown Title").strip()
        director: str = request.form.get("director", "Unknown").strip()
        year_raw: str = request.form.get("year", "")
        poster: str = request.form.get("poster", "")

        try:
            try:
                year: int = int(year_raw[:4])
            except (ValueError, TypeError):
                year = None

            if Movie.query.filter_by(user_id=user_id, name=title).first():
                msg = f'"{title}" is already in your favourites.'
            else:
                movie = Movie(
                    name=title,
                    director=director,
                    year=year or 0,
                    poster_url=poster or None,
                    user_id=user_id,
                )
                data_manager.add_movie(movie)
                msg = f'"{movie.name}" has been added to favourites.'
        except SQLAlchemyError:
            logging.exception("Database error adding movie")
            abort(500)
        except Exception:
            logging.exception("Unexpected error adding movie")
            abort(500)

        return redirect(url_for("home.home", user_id=user_id, message=msg))

    # Fallback
    return redirect(url_for("home.home", user_id=user_id))


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id: int, movie_id: int):
    """
    Delete a movie from user's.py favorites.

    :param user_id: ID of the user
    :param movie_id: ID of the movie to delete
    :return: Redirect URL to home with a status message
    :raises SQLAlchemyError: if deletion fails
    """
    User.query.get_or_404(user_id)
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()
    data_manager.delete_movie(movie_id)
    message = f'"{movie.name}" successfully deleted.'

    return redirect(url_for("home.home", user_id=user_id, message=message))


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/edit", methods=["GET"])
def edit_movie(user_id: int, movie_id: int) -> str:
    """
    Render the movie edit form fragment.

    :param user_id: ID of the user
    :param movie_id: ID of the movie to edit
    :return: HTML fragment for modal body
    """
    user = User.query.get_or_404(user_id)
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()
    current_year = datetime.now().year
    return render_template(
        "movies/edit.html", user=user, movie=movie, current_year=current_year
    )


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id: int, movie_id: int):
    """
    Update movie details from form input, using DataManager.

    :param user_id: ID of the user
    :param movie_id: ID of the movie to update
    :return: Redirect URL to home with a status message
    """
    User.query.get_or_404(user_id)

    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()
    movie.name = request.form.get("name", movie.name).strip()
    movie.director = request.form.get("director", movie.director).strip()

    year_raw = request.form.get("year", "")
    try:
        movie.year = int(year_raw[:4])
    except (ValueError, TypeError):
        # leave movie.year unchanged on error
        pass

    try:
        updated = data_manager.update_movie(movie)
        message = f'"{updated.name}" successfully updated.'
    except SQLAlchemyError:
        logging.exception("Error updating movie")
        abort(500)

    return redirect(url_for("home.home", user_id=user_id, message=message))

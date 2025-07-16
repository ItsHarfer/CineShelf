import logging
import os
from urllib import request

import requests
from flask import render_template, request, redirect, url_for, abort
from sqlalchemy.exc import SQLAlchemyError

from app.data_manager import DataManager
from app.users import users_bp
from app.models import User, db, Movie

data_manager = DataManager(db)


@users_bp.route("/", methods=["GET", "POST"])
def add_user():
    """
    Handle adding a new user. If POST, validate and add user, then redirect with a message.
    If GET, render the add user form, optionally as a partial for modal display.
    """
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            message = "Username is required."
            return redirect(url_for("users.index", message=message))

        user = data_manager.create_user(username)

        message = f"User {user.name} added successfully."
        return redirect(url_for("home.home", message=message))

    # GET
    message = request.args.get("message")
    if request.args.get("modal"):
        return render_template("partials/users/add.html", message=message)

    # Fallback
    return render_template("fallback/users/add.html", message=message)


@users_bp.route("/<int:user_id>/movies", methods=["GET", "POST"])
def user_movies(user_id):
    """
    If called with ?modal=1, returns just the partial for the modal body.
    Otherwise falls back to a full-page render.
    Uses DataManager to fetch the movies.
    """

    # ensure user exists
    user = User.query.get_or_404(user_id)

    # Add movie to favourites
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()

        if not title:
            msg = "Please provide a movie title."
            return redirect(
                url_for(
                    "users.user_movies",
                    user_id=user_id,
                    message=msg,
                    modal=request.args.get("modal"),
                )
            )
        try:
            data = fetch_omdb_data(title)
            movie = build_movie_from_omdb(data, user_id)
            data_manager.add_movie(movie)
            msg = f"Added “{movie.name}” to your favorites!"
        except ValueError as ve:
            msg = f"OMDb error: {ve}"
        except requests.RequestException:
            msg = "Failed to fetch movie info. Please try again later."
        except Exception:
            logging.exception("Error saving movie")
            msg = "Could not save movie. Please try again."
        # after successfully adding a movie, redirect back to the home page
        return redirect(url_for("home.home", message=msg))

    # GET
    movies = data_manager.get_movies(user_id)
    message = request.args.get("message")
    if request.args.get("modal"):
        action = request.args.get("action")
        if action == "add":
            return render_template(
                "partials/movies/add.html", user=user, message=message
            )
        if action == "edit":
            movie_id = request.args.get("movie_id", type=int)
            movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()
            return render_template("partials/movies/edit.html", movie=movie)
        return render_template(
            "partials/movies/movies.html", movies=movies, user=user, message=message
        )
    # Fallback
    return render_template(
        "fallback/movies/movies.html", user=user, movies=movies, message=message
    )


@users_bp.route("/<int:user_id>/movies/fetch", methods=["GET"])
def fetch_movie_for_modal(user_id):
    title = request.args.get("title", "").strip()
    if not title:
        abort(400, "Title required")

    User.query.get_or_404(user_id)

    try:
        data = fetch_omdb_data(title)
    except ValueError as ve:
        return f'<div class="alert alert-warning">OMDb error: {ve}</div>', 200
    except requests.RequestException:
        return '<div class="alert alert-danger">Fehler beim Abruf.</div>', 200

    return render_template("partials/movies/details.html", movie=data, user_id=user_id)


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):

    # fetch the existing movie or 404
    movie = Movie.query.get_or_404(movie_id)

    # extract form data
    name = (request.form.get("name") or movie.name).strip()
    director = (request.form.get("director") or movie.director).strip()
    year_str = request.form.get("year") or movie.year
    user_id = request.form.get("user_id") or movie.user_id
    poster_url = (request.form.get("poster_url") or movie.poster_url).strip() or None

    # validate required fields
    if not name or not director or not year_str or not user_id:
        msg = "Name, director, user and year are required."
        return redirect(url_for("home.home", message=msg))

    # parse year
    try:
        year = int(year_str)
    except ValueError:
        msg = "Year must be a number."
        return redirect(url_for("home.home", message=msg))

    # apply updates
    movie.name = name
    movie.director = director
    movie.year = year
    movie.user_id = user_id
    movie.poster_url = poster_url

    try:
        # commit to DB
        data_manager.update_movie(movie)
    except SQLAlchemyError:
        logging.exception("Error updating movie")
        msg = "Could not update movie. Please try again."
        return redirect(url_for("home.home", message=msg))

    msg = f'Movie "{movie.name}" updated successfully.'
    return redirect(url_for("home.home", message=msg))


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    # ensure user exists
    User.query.get_or_404(user_id)
    # ensure the movie belongs to that user
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()

    try:
        # remove via DataManager (or directly via db.session)
        data_manager.delete_movie(movie_id)
        msg = f'Movie "{movie.name}" removed from your favorites.'
    except Exception:
        logging.exception("Error deleting movie")
        msg = "Could not delete movie. Please try again."

    return redirect(url_for("home.home", message=msg))


@users_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """
    Delete a user and all their movies.
    """
    try:
        user = User.query.get_or_404(user_id)
        data_manager.delete_user(user_id)
        message = f"User {user.name} deleted successfully."
        return redirect(url_for("home.home", message=message))
    except SQLAlchemyError:
        logging.exception("Error deleting user")
        msg = "Could not delete user. Please try again."
        return redirect(url_for("home.home", message=msg))


def fetch_omdb_data(title: str) -> dict:
    """
    Query OMDb API for the given movie title.
    Raises ValueError if the movie isn't found.
    Raises requests.RequestException on network/API errors.
    """
    api_key = os.getenv("OMDB_API_KEY")
    if not api_key:
        logging.error("OMDB_API_KEY not set in environment")
        abort(500, "Movie service unavailable.")
    resp = requests.get(
        "http://www.omdbapi.com/", params={"apikey": api_key, "t": title}
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("Response") != "True":
        raise ValueError(data.get("Error", "Movie not found"))
    return data


def build_movie_from_omdb(data: dict, user_id: int) -> Movie:
    """
    Construct a Movie instance from OMDb JSON data.
    """
    try:
        year = int(data.get("Year", "")[:4])
    except (ValueError, TypeError):
        year = 0

    poster = data.get("Poster")
    return Movie(
        name=data.get("Title", "Unknown Title"),
        director=data.get("Director", "Unknown"),
        year=year,
        poster_url=(poster if poster and poster != "N/A" else None),
        user_id=user_id,
    )

import logging

from urllib import request


from flask import render_template, request, redirect, url_for, abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError

from app.data_manager import DataManager
from app.models import User, db, Movie
from app.utils import fetch_omdb_data, build_movie_from_omdb

users_bp = Blueprint("users", __name__, url_prefix="/users")
data_manager = DataManager(db)


@users_bp.route("/add", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        user = data_manager.create_user(username)
        message = f"User «{user.name}» successfully created."
        return redirect(url_for("home.home", user_id=user.id, message=message))

    # GET
    return render_template("users/add.html")


@users_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        data_manager.delete_user(user_id)
        message = f"User «{user.name}» deleted."
    except SQLAlchemyError:
        logging.exception("Error deleting user")
        message = "Error during user deletion."
    return redirect(url_for("home.home", message=message))


@users_bp.route("/<int:user_id>/movies", methods=["GET", "POST"])
def user_movies(user_id):
    user = User.query.get_or_404(user_id)

    # GET modal=1&action=add: render the search/add template
    if request.method == "GET" and request.args.get("modal"):
        title = request.args.get("title", "").strip()
        data = fetch_omdb_data(title) if title else None
        return render_template(
            "movies/add.html", user=user, data=data, message=request.args.get("message")
        )

    # POST: we now have all OMDb fields in the form
    if request.method == "POST":
        # pull them straight from the form
        title = request.form.get("title", "").strip() or "Unknown Title"
        director = request.form.get("director", "Unknown").strip()
        plot = request.form.get("plot", "")
        year_raw = request.form.get("year", "")
        poster = request.form.get("poster", "")

        try:
            # parse year or default
            try:
                year = int(year_raw[:4])
            except (ValueError, TypeError):
                year = None

            movie = Movie(
                name=title,
                director=director,
                year=year or 0,
                poster_url=poster or None,
                user_id=user_id,
            )
            data_manager.add_movie(movie)
            msg = f"“{movie.name}” has been added to favorites."
        except Exception:
            logging.exception("Error adding movie")
            msg = "An error occurred while adding the movie."

        return redirect(url_for("home.home", user_id=user_id, message=msg))

    return redirect(url_for("home.home", user_id=user_id))


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    User.query.get_or_404(user_id)
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()
    try:
        data_manager.delete_movie(movie_id)
        msg = f"«{movie.name}» successfully deleted."
    except Exception:
        logging.exception("Error deleting movie")
        msg = "Fehler beim Löschen."
    return redirect(url_for("home.home", user_id=user_id, message=msg))


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/edit", methods=["GET"])
def edit_movie(user_id, movie_id):
    # Sicherstellen, dass User und Movie existieren
    user = User.query.get_or_404(user_id)
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()
    # Liefere nur das Fragment für den Modal-Body zurück
    return render_template("movies/edit.html", user=user, movie=movie)


@users_bp.route("/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    # 1) Validierung
    User.query.get_or_404(user_id)
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()
    # 2) Felder aus dem Formular auslesen und setzen
    movie.name = request.form.get("name", movie.name).strip()
    movie.director = request.form.get("director", movie.director).strip()
    year_raw = request.form.get("year", "")
    try:
        movie.year = int(year_raw[:4])
    except (ValueError, TypeError):
        pass
    # 3) Speichern und Redirect
    try:
        db.session.commit()
        msg = f"«{movie.name}» erfolgreich aktualisiert."
    except Exception:
        logging.exception("Fehler beim Aktualisieren")
        msg = "Fehler beim Speichern der Änderungen."
    return redirect(url_for("home.home", user_id=user_id, message=msg))

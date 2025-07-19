# File: data/data_seed.py
"""
Purpose:
    Initialize and seed the database with sample users and movies, fetching poster URLs from OMDB API.

Features:
    - Drops and recreates all tables
    - Creates two sample users (Alice and Bob)
    - Defines and adds a list of movies for each user
    - Fetches movie poster URLs via OMDB API
    - Prints a status message upon completion

Exceptions:
    - requests.RequestException: on network errors during API calls
    - ValueError: if response JSON parsing fails
    - SQLAlchemyError: on database transaction failures

Author: Martin Haferanke
Date: 2025-07-18

"""
import os
import logging

import requests
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.extentions import db
from app.models import User, Movie

load_dotenv()
OMDB_API_KEY: str = os.getenv("OMDB_API_KEY", "YOUR_OMDB_API_KEY")


def fetch_poster_by_title(title: str) -> str:
    """
    Retrieve the poster URL for a given movie title from the OMDB API.

    :param title: Movie title to search
    :return: Poster URL string or empty string if not found
    :raises requests.RequestException: when HTTP request fails
    :raises ValueError: when JSON decoding fails
    """
    url: str = f"https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException:
        logging.exception("Network error fetching OMDB data for title: %s.py", title)
        raise

    try:
        data = response.json()
    except ValueError:
        logging.exception("JSON decode error for OMDB response: %s.py", response.text)
        raise

    if data.get("Response") == "True":
        return data.get("Poster", "")
    return ""


def seed_data() -> None:
    """
    Drop and recreate database tables, seed with sample users and movies.
    :raises SQLAlchemyError: when database operations fail
    """
    app = create_app()
    with app.app_context():
        # Reset database schema
        db.drop_all()
        db.create_all()

        # Create sample users
        alice = User(name="Herbert")
        bob = User(name="Lieselotte")
        db.session.add_all([alice, bob])
        try:
            db.session.commit()
        except SQLAlchemyError:
            logging.exception("Error committing initial users")
            db.session.rollback()
            raise

        # Define movies for each user
        alice_movies = [
            ("Inception", "Christopher Nolan", 2010),
            ("The Matrix", "The Wachowskis", 1999),
            ("Interstellar", "Christopher Nolan", 2014),
            ("Arrival", "Denis Villeneuve", 2016),
            ("Her", "Spike Jonze", 2013),
            ("Ex Machina", "Alex Garland", 2014),
        ]
        bob_movies = [
            ("Pulp Fiction", "Quentin Tarantino", 1994),
            ("The Godfather", "Francis Ford Coppola", 1972),
            ("The Dark Knight", "Christopher Nolan", 2008),
            ("Fight Club", "David Fincher", 1999),
            ("Forrest Gump", "Robert Zemeckis", 1994),
            ("The Shawshank Redemption", "Frank Darabont", 1994),
        ]

        # Add movies and fetch posters
        for title, director, year in alice_movies:
            # Attempt to fetch poster URL
            try:
                poster_url: str = fetch_poster_by_title(title)
            except Exception:
                poster_url = ""
            movie = Movie(
                name=title,
                director=director,
                year=year,
                poster_url=poster_url,
                user_id=alice.id,
            )
            db.session.add(movie)

        for title, director, year in bob_movies:
            try:
                poster_url = fetch_poster_by_title(title)
            except Exception:
                poster_url = ""
            movie = Movie(
                name=title,
                director=director,
                year=year,
                poster_url=poster_url,
                user_id=bob.id,
            )
            db.session.add(movie)

        # Commit seeded movies
        try:
            db.session.commit()
        except SQLAlchemyError:
            logging.exception("Error committing seeded movies")
            db.session.rollback()
            raise

        # Notify completion
        print("[OK] Data seeded successfully.")


if __name__ == "__main__":
    seed_data()

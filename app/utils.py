import logging
import os
import requests

from app.models import Movie

OMDB_API_KEY = os.getenv("OMDB_API_KEY", "YOUR_OMDB_API_KEY")


def fetch_omdb_data(title: str) -> dict:
    """
    Fetches data for `title` from OMDb and returns a dict guaranteed
    to have Title, Year, Poster, Director, Plot (all strings, empty if none).
    """
    url = f"https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    r = requests.get(url, timeout=5)
    data = {}
    try:
        payload = r.json()
    except ValueError:
        return data

    if payload.get("Response") == "True":
        # OMDb sometimes returns "N/A" when it can't find something.
        def clean(key):
            v = payload.get(key, "")
            return "" if v == "N/A" else v

        data = {
            "Title": clean("Title"),
            "Year": clean("Year"),
            "Poster": clean("Poster"),
            "Director": clean("Director"),
            "Plot": clean("Plot"),
        }
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

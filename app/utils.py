# File: app/utils.py
"""
Purpose:
    Provide utility functions for fetching and processing movie data from the OMDb API.

Features:
    - fetch_omdb_data: Retrieve and normalize movie details from OMDb
    - build_movie_from_omdb: Construct Movie model instances from OMDb data

Exceptions:
    - JSONDecodeError: on invalid JSON response
    - requests.RequestException: on network or timeout errors

Author: Martin Haferanke
Date: 2025-07-18
"""
import logging
import os
from json import JSONDecodeError

import requests
from flask import abort

from app.models import Movie

# Load OMDb API key from environment
OMDB_API_KEY: str = os.getenv("OMDB_API_KEY", "YOUR_OMDB_API_KEY")


def fetch_omdb_data(title: str) -> dict:
    """
    Fetches and cleans data for a given movie title from the OMDb API.
    We have to clean the data because the API returns some fields as "N/A" instead of empty strings.
    This is necessary because we want to display "No movies found" in the UI when the movie is not found.

    :param title: Movie title to query
    :return: Dictionary with keys Title, Year, Poster, Director, Plot
    :raises JSONDecodeError: if response JSON is invalid
    :raises requests.RequestException: on request failure or timeout
    """
    url: str = f"https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.exception(
            "Network error fetching OMDb data for title '%s': %s", title, e
        )
        abort(500)

    try:
        payload: dict = response.json()
    except JSONDecodeError as e:
        logging.exception("JSON decode error for OMDb response: %s", response.text)
        abort(500)

    data: dict = {}
    if payload.get("Response") == "True":

        def clean(key: str) -> str:
            val = payload.get(key, "")
            return "" if val == "N/A" else val

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
    Build a Movie instance from OMDb data dictionary.

    :param data: Dictionary with OMDb fields
    :param user_id: ID of the user to associate the movie with
    :return: Unsaved Movie object
    """
    try:
        year: int = int(data.get("Year", "")[:4])
    except (ValueError, TypeError):
        year = 0

    poster_url = data.get("Poster")
    if not poster_url or poster_url == "N/A":
        poster_url = None

    return Movie(
        name=data.get("Title", "Unknown Title"),
        director=data.get("Director", "Unknown"),
        year=year,
        poster_url=poster_url,
        user_id=user_id,
    )

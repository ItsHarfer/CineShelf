# seed.py
import os
import requests
from dotenv import load_dotenv

from app import create_app
from app.extentions import db
from app.models import User, Movie

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "YOUR_OMDB_API_KEY")


def fetch_poster_by_title(title: str) -> str:
    url = f"https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    r = requests.get(url, headers=headers)
    data = (
        r.json()
        if r.headers.get("Content-Type", "").startswith("application/json")
        else {}
    )
    return data.get("Poster", "") if data.get("Response") == "True" else ""


def seed_data():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Users anlegen
        alice = User(name="Alice")
        bob = User(name="Bob")
        db.session.add_all([alice, bob])
        db.session.commit()  # ID’s werden gesetzt

        # Filme definieren
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

        # Filme anlegen und Poster abrufen
        for title, director, year in alice_movies:
            poster = fetch_poster_by_title(title)
            db.session.add(
                Movie(
                    name=title,
                    director=director,
                    year=year,
                    poster_url=poster,
                    user_id=alice.id,
                )
            )
        for title, director, year in bob_movies:
            poster = fetch_poster_by_title(title)
            db.session.add(
                Movie(
                    name=title,
                    director=director,
                    year=year,
                    poster_url=poster,
                    user_id=bob.id,
                )
            )

        db.session.commit()
        print("✅ Daten wurden erfolgreich eingespielt.")


if __name__ == "__main__":
    seed_data()

import os
import requests
from app import create_app, db
from app.models import User, Movie

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY") or "YOUR_OMDB_API_KEY"


def fetch_poster_by_title(title: str) -> str:
    """Fetch movie poster URL from OMDb API by movie title."""
    url = f"https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0",  # Some APIs block unknown agents
        "Accept": "application/json",  # Explicitly ask for JSON
    }
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        if data.get("Response") == "True":
            return data.get("Poster", "")
        else:
            print(f"❌ OMDb response error for {title}: {data.get('Error')}")
            return ""
    except Exception as e:
        print(f"❌ JSON decode failed for {title}: {e}")
        return ""


def seed_data():
    app = create_app()
    with app.app_context():
        # Delete existing data
        db.session.query(Movie).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create users
        user1 = User(name="Alice")
        user2 = User(name="Bob")
        db.session.add_all([user1, user2])
        db.session.commit()

        # Movie data
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

        # Add movies with poster URLs
        for title, director, year in alice_movies:
            poster = fetch_poster_by_title(title)
            db.session.add(
                Movie(
                    name=title,
                    director=director,
                    year=year,
                    poster_url=poster,
                    user_id=user1.id,
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
                    user_id=user2.id,
                )
            )

        db.session.commit()
        print("✅ Data seeded with posters.")


if __name__ == "__main__":
    seed_data()

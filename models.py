# app/models.py

"""
Purpose:
Defines SQLAlchemy models for Users and Movies in the MoviWeb application.
Establishes a one-to-many relationship: each Movie belongs to exactly one User.

Features:
- User model: stores a unique id and name, and has a collection of movies.
- Movie model: stores a unique id, title, director, release year, poster URL, and a foreign key to User.

Author: Martin Haferanke
Date: 2025-07-11
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

# Initialize the SQLAlchemy extension
db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user in the application.

    This class provides the structure for storing user information, including
    their unique identifier, name, and any associated movies. It is designed
    to integrate with an SQLAlchemy database and supports a one-to-many
    relationship with the `Movie` class. The purpose of this class is to
    manage user-specific data within the application context.

    :ivar id: Unique identifier for the user.
    :type id: int
    :ivar name: Name of the user.
    :type name: str
    :ivar movies: Collection of movies associated with the user.
    :type movies: sqlalchemy.orm.dynamic.AppenderQuery
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # Define one-to-many relationship: one User can have many Movies
    movies = db.relationship(
        "Movie",
        backref=backref("user", lazy=True),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return self.name


class Movie(db.Model):
    """
    Represents a movie record in the database.

    This class maps to the "movies" table in the database. It stores information
    about a movie, including its name, director, release year, and an optional
    URL for its poster. Each movie is associated with a user, establishing a
    relationship via the `user_id` attribute. The class also provides string
    representations for debugging and display purposes.

    :ivar id: The unique identifier for the movie.
    :type id: int
    :ivar name: The name/title of the movie.
    :type name: str
    :ivar director: The director of the movie.
    :type director: str
    :ivar year: The release year of the movie.
    :type year: int
    :ivar poster_url: The URL of the movie poster (if provided).
    :type poster_url: str or None
    :ivar user_id: The id of the user associated with this movie.
    :type user_id: int
    """

    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    director = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String, nullable=True)

    # Link this Movie to its owning User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Movie id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return f"{self.name} ({self.year}) by {self.director}"

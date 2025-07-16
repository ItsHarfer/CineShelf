import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

from app.models import User, Movie


class DataManager:
    """
    Service class to handle basic CRUD operations for Users and Movies.
    """

    def __init__(self, db: SQLAlchemy):
        """
        :param db: The SQLAlchemy instance used for sessions.
        """
        self.db = db

    def create_user(self, name: str) -> User:
        """
        Create a new User with the given name and persist it to the database.

        :param name: Full name of the new user.
        :return: The newly created User object.
        :raises SQLAlchemyError: If the operation fails.
        """
        user = User(name=name)
        try:
            self.db.session.add(user)
            self.db.session.commit()
            return user
        except SQLAlchemyError as e:
            logging.exception(f"Database commit failed: {e}")
            self.db.session.rollback()
            raise

    def delete_user(self, user_id: int):
        """
        Delete a User instance from the database.
        """
        try:
            user = User.query.get(user_id)
            self.db.session.delete(user)
            self.db.session.commit()
        except SQLAlchemyError:
            logging.error("Failed to delete user with ID %d", user_id)

    def get_users(self) -> List[User]:
        """
        Retrieve all users from the database.

        :return: List of User objects.
        """
        return self.db.session.query(User).order_by(User.name).all()

    def get_movies(self, user_id: int) -> List[Movie]:
        """
        Retrieve all movies belonging to a specific user.

        :param user_id: The ID of the user whose movies to fetch.
        :return: List of Movie objects for that user.
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, movie: Movie) -> Movie:
        """
        Add a new Movie instance to the database (and link it to its User via movie.user_id).

        :param movie: A Movie object with its `user_id` already set.
        :return: The newly added Movie object.
        :raises SQLAlchemyError: If the operation fails.
        """
        try:
            self.db.session.add(movie)
            self.db.session.commit()
            return movie
        except SQLAlchemyError:
            self.db.session.rollback()
            raise

    def update_movie(self, movie):
        """
        Merge the given Movie instance into the session and commit.
        """
        try:
            # merge() will INSERT if new or UPDATE if existing
            self.db.session.merge(movie)
            self.db.session.commit()
            return movie
        except SQLAlchemyError as e:
            logging.exception("Failed to update movie: %s", e)
            self.db.session.rollback()
            raise

    def delete_movie(self, movie_id):
        """
        Delete a Movie instance from the database.

        :param movie_id: The ID of the Movie to delete.
        """
        try:
            movie = Movie.query.get(movie_id)
            self.db.session.delete(movie)
            self.db.session.commit()
        except SQLAlchemyError:
            logging.error("Failed to delete movie with ID %d", movie_id)

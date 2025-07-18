# File: app/data_manager.py
"""
Purpose:
    Service class to handle CRUD operations for User and Movie models,
    interfacing with the SQLAlchemy session.

Features:
    - Create, retrieve, update, and delete Users
    - Retrieve, add, update, and delete Movies for a user

Required Modules:
    - logging: application logging
    - sqlalchemy.exc.SQLAlchemyError: database error handling
    - flask_sqlalchemy.SQLAlchemy: session management
    - app.models: User, Movie model classes

Exceptions:
    - SQLAlchemyError: on database operation failures

Author: Martin Haferanke
Date: 2025-07-18
"""
import logging
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

from app.models import User, Movie


class DataManager:
    """
    Handles operations related to users and movies using a SQLAlchemy instance.

    DataManager is responsible for creating, updating, retrieving, and deleting
    users and movies in the database. It serves as an abstraction layer between
    the application logic and the database operations, leveraging SQLAlchemy
    to manage persistence.
    """

    def __init__(self, db: SQLAlchemy) -> None:
        """
        Initialize DataManager with a SQLAlchemy instance.

        :param db: The SQLAlchemy instance used for database sessions.
        """
        self.db = db

    def create_user(self, name: str) -> User:
        """
        Create and persist a new user.

        :param name: Username to create.
        :return: Created User object.
        :raises SQLAlchemyError: if commit fails.
        """
        user = User(name=name)
        try:
            self.db.session.add(user)
            self.db.session.commit()
            return user
        except SQLAlchemyError as e:
            logging.exception("Database commit failed when creating user: %s", e)
            self.db.session.rollback()
            raise

    def delete_user(self, user_id: int) -> None:
        """
        Delete a user by ID.

        :param user_id: ID of the user to delete.
        :raises SQLAlchemyError: if commit fails.
        """
        try:
            user = User.query.get(user_id)
            if user is None:
                logging.warning("User with ID %d not found for deletion.", user_id)
                return

            self.db.session.delete(user)
            self.db.session.commit()
        except SQLAlchemyError as e:
            logging.exception("Failed to delete user with ID %d: %s", user_id, e)
            self.db.session.rollback()
            raise

    def get_users(self) -> List[User]:
        """
        Retrieve all users, ordered by name.

        :return: List of User objects.
        """
        # Query all users sorted alphabetically
        return self.db.session.query(User).order_by(User.name).all()

    def get_movies(self, user_id: int) -> List[Movie]:
        """
        Retrieve all movies for a specific user.

        :param user_id: ID of the user.
        :return: List of Movie objects.
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, movie: Movie) -> Movie:
        """
        Add a new movie to the database.

        :param movie: Movie instance with user_id set.
        :return: The added Movie object.
        :raises SQLAlchemyError: if commit fails.
        """
        try:
            self.db.session.add(movie)
            self.db.session.commit()
            return movie
        except SQLAlchemyError as e:
            logging.exception("Failed to add movie '%s': %s", movie.name, e)
            self.db.session.rollback()
            raise

    def update_movie(self, movie: Movie) -> Movie:
        """
        Update an existing movie or insert if new.

        :param movie: Movie instance to merge.
        :return: The merged Movie object.
        :raises SQLAlchemyError: if commit fails.
        """
        try:
            merged = self.db.session.merge(movie)
            self.db.session.commit()
            return merged
        except SQLAlchemyError as e:
            logging.exception("Failed to update movie '%s': %s", movie.name, e)
            self.db.session.rollback()
            raise

    def delete_movie(self, movie_id: int) -> None:
        """
        Delete a movie by ID.

        :param movie_id: ID of the movie to delete.
        :raises SQLAlchemyError: if commit fails.
        """
        try:
            movie = Movie.query.get(movie_id)
            if movie is None:
                logging.warning("Movie with ID %d not found for deletion.", movie_id)
                return

            self.db.session.delete(movie)
            self.db.session.commit()
        except SQLAlchemyError as e:
            logging.exception("Failed to delete movie with ID %d: %s", movie_id, e)
            self.db.session.rollback()
            raise

# File: app/config.py
"""
Purpose:
    Define configuration classes for different environments (development, testing, production),
    load environment variables, and provide a mapping for easy lookup.

Features:
    - BaseConfig with default settings for security, SQLAlchemy, and Flask
    - DevelopmentConfig enabling debug mode
    - TestingConfig using in-memory database and disabling external API calls
    - ProductionConfig optimizing for production deployment
    - `config_by_name` mapping for selecting configurations by name

Required Modules:
    - os: file paths and environment variable access
    - dotenv.load_dotenv: load variables from .env file

Author: Martin Haferanke
Date: 2025-07-18
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    """
    Base configuration with default settings for all environments.

    Attributes:
        SECRET_KEY (str): Application secret key for session signing.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable SQLAlchemy event system.
        SQLALCHEMY_ECHO (bool): Toggle SQL query logging.
        SQLALCHEMY_DATABASE_URI (str): Database connection URI.
        DEBUG (bool): Flask debug flag.
        TESTING (bool): Flask testing flag.
    """

    # Security for production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")

    # Disable SQLAlchemy modification tracking for performance
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False

    # Construct default SQLite database URI if none provided
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(basedir, os.pardir, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(instance_dir, 'movies.sqlite')}"
    )

    # Flask settings
    DEBUG: bool = False
    TESTING: bool = False


class DevelopmentConfig(BaseConfig):
    """
    Development configuration: enables debug mode.

    Overrides:
        DEBUG: Enable Flask debug mode.
    """

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = False  # Optionally log SQL statements


class TestingConfig(BaseConfig):
    """
    Testing configuration: uses in-memory database and disables external API usage.

    Overrides:
        TESTING: Enable Flask testing mode.
        TESTING: Enable Flask testing mode.
        SQLALCHEMY_DATABASE_URI: Use SQLite in-memory database.
        OPENAI_API_KEY: None to prevent real API calls.
    """

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    OPENAI_API_KEY = None  # Prevent external API calls during tests


class ProductionConfig(BaseConfig):
    """
    Production configuration: disables debug and optimizes database usage.

    Overrides:
        SQLALCHEMY_DATABASE_URI: Use provided DATABASE_URL or default SQLite file.
        SQLALCHEMY_ECHO: Disable query logging in production.
    """

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/movies.sqlite')}",
    )
    SQLALCHEMY_ECHO: bool = False


# Mapping for easy configuration lookup by environment name
config_by_name: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

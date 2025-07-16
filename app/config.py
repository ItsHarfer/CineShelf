import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration with default settings."""

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False

    # Dynamically determine base directory and construct DB URI
    _base_dir: str = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(_base_dir, 'data/movies.sqlite')}"
    )

    # Flask settings
    DEBUG: bool = False
    TESTING: bool = False


class DevelopmentConfig(BaseConfig):
    """Development configuration: enables debug mode."""

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = False  # Log all SQL statements if needed


class TestingConfig(BaseConfig):
    """Testing configuration: uses in-memory DB and disables API usage."""

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    OPENAI_API_KEY: None = None  # Prevent real API calls during tests


class ProductionConfig(BaseConfig):
    """Production configuration: disables debug and optimizes DB usage."""

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/movies.sqlite')}",
    )
    SQLALCHEMY_ECHO: bool = False  # Disable SQL logging in production


# Mapping for easy lookup by environment name
config_by_name: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

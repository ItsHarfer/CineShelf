# File: app/__init__.py
"""
Purpose:
    Create and configure the Flask application, initialize extensions,
    set up template loaders, register blueprints, error handlers, and logging.

Features:
    - Load environment variables
    - Configure app from settings
    - Initialize SQLAlchemy and rate limiter
    - Automatically create database tables
    - Configure Jinja2 loaders for partials and fallback templates
    - Register home and users blueprints
    - Define HTTP error handlers for 404, 403, and 500 errors
    - Set up rotating file logging

Required Modules:
    - os: file path operations
    - logging, logging.handlers.RotatingFileHandler: application logging
    - flask: Flask, render_template
    - dotenv.load_dotenv: environment variable loading
    - jinja2.FileSystemLoader, jinja2.ChoiceLoader: template loading
    - sqlalchemy.exc: SQLAlchemyError
    - app.config.config_by_name: configuration mapping
    - app.extentions.db: SQLAlchemy instance
    - app.extentions.limiter: rate limiter instance
    - app.blueprints.home.home_bp: home blueprint
    - app.blueprints.users.users_bp: users blueprint

Exceptions:
    - OSError: on filesystem errors when creating log directory

Author: Martin Haferanke
Date: 2025-07-18
"""
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from dotenv import load_dotenv
from jinja2 import ChoiceLoader, FileSystemLoader

from app.config import config_by_name
from app.extentions import db, limiter
from app.blueprints.home import home_bp
from app.blueprints.users import users_bp


def create_app(
    config_name: str | None = None,
    template_folder: str | None = None,
    static_folder: str | None = None,
) -> Flask:
    """
    Factory to create and configure the Flask app instance.

    :param config_name: key to select configuration (default: 'default')
    :type config_name: str | None
    :param template_folder: custom template folder path
    :type template_folder: str | None
    :param static_folder: custom static folder path
    :type static_folder: str | None
    :return: Configured Flask application
    :rtype: Flask
    :raises OSError: if log directory cannot be created
    """
    # Load environment variables
    load_dotenv()

    # Initialize Flask
    app = Flask(
        __name__,
        template_folder=template_folder or "app/templates",
        static_folder=static_folder or "app/static",
    )

    # Apply configuration
    cfg = config_by_name.get(config_name or "default")
    app.config.from_object(cfg)

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()

    # Configure Jinja2 loaders: default -> partials -> fallback
    root = app.root_path
    partials_path = os.path.join(root, "templates", "partials")
    fallback_path = os.path.join(root, "templates", "fallback")
    app.jinja_loader = ChoiceLoader(
        [
            app.jinja_loader,
            FileSystemLoader(partials_path),
            FileSystemLoader(fallback_path),
        ]
    )

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(users_bp, url_prefix="/users")

    # Register error handlers
    @app.errorhandler(404)
    def handle_404(e: Exception) -> tuple:
        """Render 404 page."""
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def handle_403(e: Exception) -> tuple:
        """Render 403 page."""
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def handle_500(e: Exception) -> tuple:
        """Render 500 page."""
        return render_template("errors/500.html"), 500

    # Setup rotating log handler
    log_dir = os.path.join(os.path.dirname(__file__), os.pardir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "cineshelf.log")
    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024, backupCount=3)
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    )
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    return app

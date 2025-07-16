from flask import Flask
from dotenv import load_dotenv
from jinja2 import FileSystemLoader, ChoiceLoader

from .extentions import db
from .config import config_by_name
from .events import _enable_sqlite_fk

from app.extentions import limiter

from .blueprints.home import home_bp
from .blueprints.users import users_bp

import logging
from logging.handlers import RotatingFileHandler
import os


def create_app(
    config_name: str = None,
    template_folder: str | None = None,
    static_folder: str | None = None,
) -> Flask:

    load_dotenv()
    app = Flask(
        __name__,
        template_folder=template_folder or "app/templates",
        static_folder=static_folder or "app/static",
    )
    cfg = config_by_name.get(config_name or "default")
    app.config.from_object(cfg)

    # Extensions
    db.init_app(app)
    limiter.init_app(app)

    # Create DB tables in application context
    with app.app_context():
        db.create_all()

    # 1) Path to /templates/fallback
    fallback_path = os.path.join(app.root_path, "templates", "fallback")

    # 2) Path to /templates/partials
    partials_path = os.path.join(app.root_path, "templates", "partials")

    # 3) Define ChoiceLoader: First Partials-Loader then Fallback-Loader
    app.jinja_loader = ChoiceLoader(
        [
            app.jinja_loader,
            FileSystemLoader(partials_path),
            FileSystemLoader(fallback_path),
        ]
    )
    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(users_bp, url_prefix="/users")

    # Logging to file

    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "cineshelf.log")

    # Set up rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=3)
    file_handler.setLevel(logging.INFO)

    # Define log format
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Attach handler to root logger
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.INFO)
    return app

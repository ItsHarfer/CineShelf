import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    load_dotenv()

    # DB path setup
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(os.path.dirname(base_dir), "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "movie.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Import models
    from app import models

    # Register blueprints
    from app.users import users_bp
    from app.routes import home_bp

    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(users_bp, url_prefix="/users")

    with app.app_context():
        db.create_all()

    return app

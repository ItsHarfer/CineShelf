# File: app/extentions.py
"""
Purpose:
    Initialize and configure common Flask extensions for the application.

Features:
    - SQLAlchemy for ORM and database session management
    - Flask-Limiter for rate limiting based on client IP

Author: Martin Haferanke
Date: 2025-07-18
"""
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()

# Rate limiter using client IP as key function
limiter = Limiter(key_func=get_remote_address)

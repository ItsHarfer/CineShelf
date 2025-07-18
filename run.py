"""
CineShelf - Your favorite movie collection in one place.

Purpose:
Entry point for initializing and running the CineShelf Flask web application.

Features:
- User Management: Create, select, and delete user profiles.
- Movie Collection: Search OMDb, add to favorites, edit details, and remove movies.
- Responsive UI: Bootstrap-based layout with floating action button and modal dialogs.
- API Integration: Normalize OMDb data and handle missing/N/A fields.
- Rate Limiting: Protect endpoints with per-IP limits (10 requests/minute).
- Error Handling: Custom HTTP error pages (403, 404, 500) and application-level handlers.
- Logging: Rotating file logs for errors, warnings, and info events.
- Templating: Jinja2 ChoiceLoader for partials and fallback templates.

Author: Martin Haferanke
Date: 2025-07-18
"""

import os
from app import create_app

config_name: str = os.getenv("FLASK_CONFIG", "development")

base_dir = os.path.dirname(__file__)
templates = os.path.join(base_dir, "app", "templates")
statics = os.path.join(base_dir, "app", "static")

app = create_app(
    config_name=os.getenv("FLASK_CONFIG", "development"),
    template_folder=templates,
    static_folder=statics,
)

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))

    app.run(host=host, port=port, debug=True)

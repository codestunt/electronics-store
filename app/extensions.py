# app/extensions.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_mail import Mail

# Flask-Mail extension
mail = Mail()


def get_db_connection():
    """
    Create and return a PostgreSQL connection.

    - Uses Render's DATABASE_URL in production
    - Uses RealDictCursor so rows behave like dicts
    - Enforces SSL (required by Render)
    """

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Make sure it is configured in Render or your local .env file."
        )

    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor,
        sslmode="require",   # REQUIRED for Render Postgres
    )

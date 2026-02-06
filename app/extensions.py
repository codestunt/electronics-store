# app/extensions.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_mail import Mail as FlaskMail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail
from flask import current_app


# -------------------------------------------------
# SendGrid HTML receipt sender
# -------------------------------------------------
def send_receipt_email_html(to_email: str, subject: str, html_content: str):
    """
    Send HTML receipt via SendGrid.
    NEVER raises — logs only.
    """
    try:
        message = SendGridMail(
            from_email=current_app.config.get(
                "MAIL_DEFAULT_SENDER",
                "ElectroZone <no-reply@electrozone.com>"
            ),
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        sg.send(message)

    except Exception as e:
        current_app.logger.error(f"SendGrid receipt failed: {e}")


# -------------------------------------------------
# Flask-Mail extension (kept for other forms)
# -------------------------------------------------
mail = FlaskMail()


# -------------------------------------------------
# Database connection
# -------------------------------------------------
def get_db_connection():
    """
    Create and return a PostgreSQL connection.

    - Uses Render's DATABASE_URL
    - Uses RealDictCursor
    - Enforces SSL (Render requirement)
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set."
        )

    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor,
        sslmode="require",
    )

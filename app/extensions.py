import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app

# Flask-Mail (renamed safely)
from flask_mail import Mail as FlaskMail

# SendGrid (renamed safely)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail


# -------------------------------------------------
# Flask-Mail extension (used by app factory)
# -------------------------------------------------
mail = FlaskMail()


# -------------------------------------------------
# SendGrid HTML receipt sender
# -------------------------------------------------
def send_receipt_email_html(to_email: str, subject: str, html_content: str):
    """
    Send HTML receipt via SendGrid.
    NEVER raises — logs only.
    """
    try:
        current_app.logger.warning("SENDGRID: Attempting to send receipt")
        current_app.logger.warning(f"SENDGRID: To={to_email}")

        message = SendGridMail(
            from_email=current_app.config.get(
                "MAIL_DEFAULT_SENDER",
                "ElectroZone <joemtaika@gmail.com>"
            ),
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)

        current_app.logger.warning(
            f"SENDGRID RESPONSE STATUS: {response.status_code}"
        )

    except Exception as e:
        current_app.logger.error(f"SENDGRID FAILED: {e}")


# -------------------------------------------------
# Database helper (unchanged)
# -------------------------------------------------
def get_db_connection():
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

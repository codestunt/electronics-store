import os
from flask import current_app
from flask_mail import Mail, Message
import psycopg2
from psycopg2.extras import RealDictCursor

# -------------------------------------------------
# Flask-Mail extension
# -------------------------------------------------
mail = Mail()


# -------------------------------------------------
# Email sender (HTML receipts)
# -------------------------------------------------
def send_receipt_email_html(to_email: str, subject: str, html_content: str):
    """
    Send HTML email using Gmail SMTP.
    NEVER crashes checkout.
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_content
        )
        mail.send(msg)

        current_app.logger.warning(
            f"EMAIL SENT SUCCESSFULLY → {to_email}"
        )

        return True

    except Exception as e:
        current_app.logger.error(f"EMAIL FAILED: {e}")
        return False


# -------------------------------------------------
# Database helper
# -------------------------------------------------
def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    print("DEBUG → DATABASE_URL =", database_url)

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")

    return psycopg2.connect(
        dsn=database_url,
        cursor_factory=RealDictCursor,
        sslmode="require"
    )


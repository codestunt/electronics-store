
# VERSION: 2026-02-05-RENDER-CACHE-BUST


from flask import Flask
from dotenv import load_dotenv
import os

from .extensions import mail
from .routes import routes
from .routes_payments import bp_pay


def create_app():
    """
    Application factory: creates and configures the Flask app.
    """

    # Load environment variables
    load_dotenv(override=True)

    app = Flask(__name__)

    # -------------------------------------------------
    # Base URL (IMPORTANT for Stripe redirects)
    # -------------------------------------------------
    app.config["BASE_URL"] = os.environ.get(
        "BASE_URL",
        "http://127.0.0.1:5000"
    )

    # -------------------------------------------------
    # Core Flask secret key
    # -------------------------------------------------
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-replace-me"
    )

    # -------------------------------------------------
    # Stripe configuration
    # -------------------------------------------------
    app.config["STRIPE_SECRET_KEY"] = os.environ.get("STRIPE_SECRET_KEY")
    app.config["STRIPE_PUBLISHABLE_KEY"] = os.environ.get("STRIPE_PUBLISHABLE_KEY")

    # -------------------------------------------------
    # PayPal configuration
    # -------------------------------------------------
    app.config["PAYPAL_CLIENT_ID"] = os.environ.get("PAYPAL_CLIENT_ID")
    app.config["PAYPAL_SECRET"] = os.environ.get("PAYPAL_SECRET")
    app.config["PAYPAL_MODE"] = os.environ.get("PAYPAL_MODE", "sandbox")

    # -------------------------------------------------
    # Email configuration (Flask-Mail)
    # -------------------------------------------------
    app.config["MAIL_SUPPRESS_SEND"] = False


    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = (
        f"ElectroZone <{os.environ.get('MAIL_USERNAME')}>"
    )

    # -------------------------------------------------
    # Initialise extensions
    # -------------------------------------------------
    mail.init_app(app)

    # -------------------------------------------------
    # Register blueprints
    # -------------------------------------------------
    app.register_blueprint(routes)
    app.register_blueprint(bp_pay, url_prefix="/pay")

    return app

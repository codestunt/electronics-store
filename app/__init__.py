
# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
import os

from .extensions import mail
from .routes import routes
from .routes_payments import bp_pay

load_dotenv()



def create_app():
    """
    Application factory: creates and configures the Flask app.
    """
    # Load environment variables from a .env file (if present)
    # Values in .env override shell environment by default here.
    load_dotenv(override=True)

    app = Flask(__name__)   

    app.config["BASE_URL"] = os.environ.get(
    "BASE_URL",
    "http://127.0.0.1:5000"
)


    app.config["MAIL_SUPPRESS_SEND"] = (
    os.environ.get("MAIL_SUPPRESS_SEND", "false").lower() == "true"
)


    # ------------------------------------------------------------------
    # Core Flask secret key
    # ------------------------------------------------------------------
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-replace-me")

    # ------------------------------------------------------------------
    # Stripe configuration
    # ------------------------------------------------------------------
    # These should be set in your .env as:
    #   STRIPE_SECRET_KEY=sk_test_...
    #   STRIPE_PUBLISHABLE_KEY=pk_test_...
    app.config["STRIPE_SECRET_KEY"] = os.environ.get(
        "STRIPE_SECRET_KEY",
        "sk_test_your_real_test_secret_key_here",
    )
    app.config["STRIPE_PUBLISHABLE_KEY"] = os.environ.get(
        "STRIPE_PUBLISHABLE_KEY",
        "pk_test_your_real_test_publishable_key_here",
    )


    # ------------------------------------------------------------------
    # PayPal configuration  ✅ NEW
    # ------------------------------------------------------------------
    # These are already in your .env:
    #   PAYPAL_CLIENT_ID=...
    #   PAYPAL_SECRET=...
    #   PAYPAL_MODE=sandbox
    app.config["PAYPAL_CLIENT_ID"] = os.environ.get("PAYPAL_CLIENT_ID")
    app.config["PAYPAL_SECRET"] = os.environ.get("PAYPAL_SECRET")
    app.config["PAYPAL_MODE"] = os.environ.get("PAYPAL_MODE", "sandbox")

    # ------------------------------------------------------------------
    # MySQL configuration (your existing values)
    # ------------------------------------------------------------------
    

    # ------------------------------------------------------------------
    # Email configuration (Flask-Mail)
    # ------------------------------------------------------------------
    # Recommended to put these in .env:
    #   MAIL_SERVER=smtp.gmail.com
    #   MAIL_PORT=587
    #   MAIL_USE_TLS=true
    #   MAIL_USERNAME=your_email@gmail.com
    #   MAIL_PASSWORD=your_app_password
    #   MAIL_DEFAULT_SENDER="ElectroZone <your_email@gmail.com>"
    # ------------------------------------------------------------------
# Email configuration (Flask-Mail)
# ------------------------------------------------------------------
app.config["MAIL_SUPPRESS_SEND"] = os.getenv("MAIL_SUPPRESS_SEND") == "1"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = (
    f"ElectroZone <{os.environ.get('MAIL_USERNAME')}>"
)


    # ------------------------------------------------------------------
    # Initialise extensions
    # ------------------------------------------------------------------
    
    mail.init_app(app)

    # ------------------------------------------------------------------
    # Register blueprints
    # ------------------------------------------------------------------
    app.register_blueprint(routes)                     # core site routes
    app.register_blueprint(bp_pay, url_prefix="/pay")  # payment routes (/pay/...)

    return app

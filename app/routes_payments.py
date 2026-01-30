
from flask import (
    Blueprint,
    request,
    jsonify,
    current_app,
    session,
    redirect,
    url_for,
    flash,
    render_template,
)
import stripe
import requests
import time
from datetime import datetime, timedelta
import uuid
import os

from app.extensions import mail
from flask_mail import Message


bp_pay = Blueprint("payments", __name__)  # registered with url_prefix="/pay"


# -------------------------------
# Helpers
# -------------------------------

def generate_order_id():
    # Example: EZ-3F8C1AB920
    return "EZ-" + uuid.uuid4().hex[:10].upper()


def send_order_receipt_email(to_email, order_id, order_items, order_total, est_delivery_date):
    """
    Send a nicely formatted HTML receipt email using Flask-Mail (real SMTP).
    """

    if not to_email:
        current_app.logger.info("[EMAIL] No destination email, skipping receipt.")
        return

    # Build the HTML body from your Jinja template
    html_body = render_template(
        "email_order_receipt.html",
        order_id=order_id,
        order_items=order_items,
        order_total=order_total,
        est_delivery_date=est_delivery_date,
    )

    # Optional simple text version (fallback)
    text_body = f"""Thank you for your order!

Order ID: {order_id}
Order total: ${order_total:,.2f}
Order date: {est_delivery_date}

You can view your full receipt by logging into ElectroZone.
"""

    msg = Message(
        subject=f"Your ElectroZone Receipt · {order_id}",
        recipients=[to_email],
    )
    msg.body = text_body
    msg.html = html_body

    try:
        current_app.logger.info("[EMAIL] Sending receipt via Flask-Mail to %s", to_email)
        mail.send(msg)
        current_app.logger.info("[EMAIL] Receipt sent successfully to %s", to_email)
    except Exception as e:
        current_app.logger.exception("[EMAIL] Error sending receipt email: %s", e)


# -------------------------------
# Stripe helpers (already working)
# -------------------------------

def _cart_to_line_items(cart):
    """Convert cart into Stripe line_items."""
    line_items = []

    if not cart:
        return line_items

    for it in cart:
        name = str(it.get("name") or "Item")
        qty = int(it.get("quantity") or 1)
        price = float(it.get("price") or 0.0)
        unit_amount = max(0, int(round(price * 100)))  # cents

        line_items.append(
            {
                "quantity": qty,
                "price_data": {
                    "currency": "aud",
                    "unit_amount": unit_amount,
                    "product_data": {"name": name},
                },
            }
        )
    return line_items


def _cart_total(cart):
    """Total cart value as a decimal (for PayPal)."""
    total = 0.0
    for it in cart:
        qty = int(it.get("quantity") or 1)
        price = float(it.get("price") or 0.0)
        total += qty * price
    return round(total, 2)


@bp_pay.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """
    Stripe: create Checkout Session and return session.id as JSON.
    Called from cart.html when user chooses Credit/Debit Card.
    """
    secret = current_app.config.get("STRIPE_SECRET_KEY")
    if not secret:
        return jsonify({"error": "STRIPE_SECRET_KEY not configured"}), 500

    stripe.api_key = secret

    cart = session.get("cart", [])
    line_items = _cart_to_line_items(cart)
    if not line_items:
        return jsonify({"error": "Your cart is empty."}), 400

    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()

    # 🔹 Prefer the login email if available
    login_email = session.get("user_email") or session.get("email")
    if login_email:
        email = login_email

    # Store the final email in session for the receipt page
    if email:
        session["user_email"] = email
        session.modified = True

    try:
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=line_items,
            success_url=url_for("payments.pay_success", _external=True),
            cancel_url=url_for("payments.pay_cancel", _external=True),
            customer_email=email or None,
            metadata={
                "full_name": full_name,
                "shipping_address": address,
            },
        )
        return jsonify({"id": checkout_session.id})

    except Exception as e:
        current_app.logger.exception("Error creating Stripe Checkout Session")
        return jsonify({"error": str(e)}), 400


@bp_pay.route("/success")
def pay_success():
    """
    Common success handler for Stripe.
    Clears the cart, stores a simple order reference and
    a full snapshot of the items for the receipt,
    then sends the user to the nice thank-you page.
    """

    # 1. Read the current cart BEFORE clearing it
    cart = session.get("cart", [])

    # 2. Build a clean summary of the order for the receipt
    order_items = []
    order_total = 0
    order_item_count = 0

    for item in cart:
        qty = item.get("quantity", 1)
        price = float(item.get("price", 0))
        subtotal = qty * price

        order_items.append({
            "name": item.get("name", "Item"),
            "qty": qty,
            "price": price,
            "subtotal": subtotal,
        })

        order_total += subtotal
        order_item_count += qty

    # 3. Store this snapshot in the session so pay_complete()
    session["last_order_items"] = order_items
    session["last_order_total"] = order_total
    session["last_order_item_count"] = order_item_count

    # 4. Simple order reference
    order_ref = f"EZ-{int(time.time())}"
    session["last_order_ref"] = order_ref

    # 5. Now it's safe to clear the cart + PayPal temporary data
    session["cart"] = []
    session.pop("paypal_order_id", None)
    session.modified = True

    # 6. Flash once (will show in layout if you already display flashes)
    flash("Payment successful. Thank you for your order!", "success")

    # 7. Go to pretty thank-you page (which sends the email)
    return redirect(url_for("payments.pay_complete"))


@bp_pay.route("/cancel")
def pay_cancel():
    """Stripe cancelled -> back to cart."""
    flash("Card payment cancelled.", "error")
    return redirect(url_for("routes.cart"))


# ---------------------------------
# PayPal helpers (Orders API v2)
# ---------------------------------

def _paypal_base_url():
    """Choose sandbox or live API base."""
    env = current_app.config.get("PAYPAL_ENV", "sandbox").lower()
    if env == "live":
        return "https://api-m.paypal.com"
    return "https://api-m.sandbox.paypal.com"


def _paypal_get_access_token():
    """Get OAuth access token from PayPal."""
    client_id = current_app.config.get("PAYPAL_CLIENT_ID")
    secret = current_app.config.get("PAYPAL_SECRET")

    if not client_id or not secret:
        raise RuntimeError("PayPal credentials not configured")

    base = _paypal_base_url()
    resp = requests.post(
        f"{base}/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_AU"},
        auth=(client_id, secret),
        data={"grant_type": "client_credentials"},
        timeout=15,
    )
    if not resp.ok:
        current_app.logger.error(
            "PayPal token error: %s %s", resp.status_code, resp.text
        )
        raise RuntimeError("Could not obtain PayPal access token")

    data = resp.json()
    return data["access_token"]


@bp_pay.route("/paypal/start", methods=["POST"])
def paypal_start():
    """
    Start a PayPal Checkout:
    - creates an order with PayPal
    - returns approval_url to the browser, which redirects the user to PayPal.
    """
    cart = session.get("cart", [])
    if not cart:
        return jsonify({"error": "Your cart is empty."}), 400

    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()

    # 🔹 Prefer the login email if available (same idea as Stripe)
    login_email = session.get("user_email") or session.get("email")
    if login_email:
        email = login_email

    # Store email in session for the receipt page
    if email:
        session["user_email"] = email
        session.modified = True

    total = _cart_total(cart)
    if total <= 0:
        return jsonify({"error": "Cart total must be greater than zero."}), 400

    try:
        access_token = _paypal_get_access_token()
        base = _paypal_base_url()

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "AUD",
                        "value": f"{total:.2f}",
                    },
                    "description": "ElectroZone order",
                }
            ],
            "application_context": {
                "brand_name": "ElectroZone",
                "landing_page": "LOGIN",
                "user_action": "PAY_NOW",
                "return_url": url_for("payments.paypal_return", _external=True),
                "cancel_url": url_for("payments.paypal_cancel", _external=True),
            },
        }

        resp = requests.post(
            f"{base}/v2/checkout/orders",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            timeout=20,
        )

        if not resp.ok:
            current_app.logger.error(
                "PayPal create order error: %s %s", resp.status_code, resp.text
            )
            return jsonify({"error": "Could not start PayPal payment."}), 400

        order = resp.json()
        # find approval link
        approval_url = None
        for link in order.get("links", []):
            if link.get("rel") == "approve":
                approval_url = link.get("href")
                break

        if not approval_url:
            current_app.logger.error("PayPal order missing approval link: %s", order)
            return jsonify({"error": "PayPal did not return an approval URL."}), 400

        # optionally store order id in session if you want to use later
        session["paypal_order_id"] = order.get("id")
        session.modified = True

        return jsonify({"approval_url": approval_url})

    except Exception as e:
        current_app.logger.exception("Error starting PayPal Checkout")
        return jsonify({"error": str(e)}), 500


@bp_pay.route("/paypal/return")
def paypal_return():
    """
    PayPal redirects here after the buyer approves the payment.
    We then CAPTURE the order (finalize the payment),
    build the same order snapshot as Stripe, and
    redirect to the common pay_complete page (which sends the email).
    """
    order_id = request.args.get("token") or request.args.get("orderID")
    if not order_id:
        flash("Missing PayPal order ID.", "error")
        return redirect(url_for("routes.cart"))

    try:
        access_token = _paypal_get_access_token()
        base = _paypal_base_url()

        resp = requests.post(
            f"{base}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            timeout=20,
        )

        if not resp.ok:
            current_app.logger.error(
                "PayPal capture error: %s %s", resp.status_code, resp.text
            )
            flash("We could not confirm your PayPal payment.", "error")
            return redirect(url_for("routes.cart"))

        capture_data = resp.json()
        current_app.logger.info("PayPal capture success: %s", capture_data)

        # --- Build the same order snapshot that Stripe does in pay_success() ---

        cart = session.get("cart", []) or []

        order_items = []
        order_total = 0
        order_item_count = 0

        for item in cart:
            qty = item.get("quantity", 1)
            price = float(item.get("price", 0))
            subtotal = qty * price

            order_items.append({
                "name": item.get("name", "Item"),
                "qty": qty,
                "price": price,
                "subtotal": subtotal,
            })

            order_total += subtotal
            order_item_count += qty

        session["last_order_items"] = order_items
        session["last_order_total"] = order_total
        session["last_order_item_count"] = order_item_count
        session["last_order_ref"] = f"EZ-{int(time.time())}"

        # clear cart
        session["cart"] = []
        session.pop("paypal_order_id", None)
        session.modified = True

        flash("PayPal payment successful. Thank you for your order!", "success")

        # Use the SAME final page (and email sending) as Stripe
        return redirect(url_for("payments.pay_complete"))

    except Exception as e:
        current_app.logger.exception("Error completing PayPal payment")
        flash("There was a problem finalising your PayPal payment.", "error")
        return redirect(url_for("routes.cart"))


@bp_pay.route("/paypal/cancel")
def paypal_cancel():
    """Buyer cancelled on PayPal UI."""
    flash("PayPal payment was cancelled.", "error")
    return redirect(url_for("routes.cart"))


@bp_pay.route("/complete")
def pay_complete():
    """
    Final landing page after successful Stripe or PayPal payment.
    Cart should already be cleared by the caller.
    """

    # 1. Unique Order ID
    order_id = generate_order_id()

    # 2. Load the order snapshot from session
    order_items = session.get("last_order_items", []) or []
    order_total = session.get("last_order_total", 0) or 0
    order_item_count = session.get("last_order_item_count", 0) or 0

    # 3. Order date (today)
    order_date = datetime.now().strftime("%d %b %Y")  # uses server local time

    # 4. Get client email
    user_email = session.get("user_email")
    print("[PAY COMPLETE] user_email from session:", user_email)

    # 5. Send the email receipt
    try:
        send_order_receipt_email(
            to_email=user_email,
            order_id=order_id,
            order_items=order_items,
            order_total=order_total,
            est_delivery_date=order_date,
        )
    except Exception as e:
        print("Error sending receipt email:", e)

    # 6. Render the beautiful confirmation page
    return render_template(
        "order_complete.html",
        order_id=order_id,
        order_items=order_items,
        order_total=order_total,
        order_items_count=order_item_count,
        est_delivery_date=order_date,
    )


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
from flask_mail import Message
from app.extensions import mail
import stripe
from datetime import datetime
import uuid

bp_pay = Blueprint("payments", __name__)


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def generate_order_id():
    return "EZ-" + uuid.uuid4().hex[:10].upper()


def _cart_to_line_items(cart):
    items = []
    for item in cart or []:
        price = int(float(item.get("price", 0)) * 100)
        qty = int(item.get("quantity", 1))
        items.append({
            "quantity": qty,
            "price_data": {
                "currency": "aud",
                "unit_amount": price,
                "product_data": {
                    "name": item.get("name", "Item"),
                },
            },
        })
    return items


# -------------------------------------------------
# Create Stripe Checkout
# -------------------------------------------------
@bp_pay.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    cart = session.get("cart", [])
    if not cart:
        return jsonify({"error": "Cart empty"}), 400

    data = request.get_json(silent=True) or {}
    email = data.get("email") or session.get("user_email")

    if email:
        session["user_email"] = email

    checkout = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=_cart_to_line_items(cart),
        customer_email=email,
        success_url=current_app.config["BASE_URL"] + "/pay/success",
        cancel_url=current_app.config["BASE_URL"] + "/pay/cancel",
    )

    return jsonify({"id": checkout.id})


# -------------------------------------------------
# SUCCESS — SEND GMAIL RECEIPT
# -------------------------------------------------
@bp_pay.route("/success")
def pay_success():
    cart = session.get("cart", [])

    items = []
    total = 0

    for it in cart:
        qty = int(it.get("quantity", 1))
        price = float(it.get("price", 0))
        subtotal = qty * price
        items.append({
            "name": it.get("name"),
            "qty": qty,
            "price": price,
            "subtotal": subtotal,
        })
        total += subtotal

    order_id = generate_order_id()
    date = datetime.now().strftime("%d %b %Y")

    # Clear cart
    session["cart"] = []

    # -------------------------------------------------
    # Gmail receipt (SAFE)
    # -------------------------------------------------
    try:
        email = session.get("user_email")
        if email:
            html = render_template(
                "email_order_receipt.html",
                order_id=order_id,
                order_items=items,
                order_total=total,
                est_delivery_date=date,
            )

            msg = Message(
                subject=f"Your ElectroZone Receipt – {order_id}",
                recipients=[email],
                html=html,
            )
            mail.send(msg)

    except Exception as e:
        current_app.logger.error(f"GMAIL RECEIPT FAILED: {e}")

    flash("Payment successful. Thank you!", "success")

    return render_template(
        "order_complete.html",
        order_id=order_id,
        order_items=items,
        order_total=total,
        est_delivery_date=date,
    )


# -------------------------------------------------
# Cancel
# -------------------------------------------------
@bp_pay.route("/cancel")
def pay_cancel():
    flash("Payment cancelled.", "error")
    return redirect(url_for("routes.cart"))


@bp_pay.route("/test-gmail")
def test_gmail():
    try:
        msg = Message(
            subject="✅ ElectroZone Gmail Test",
            recipients=["joemtaika@gmail.com"],
            body="If you received this email, Gmail + Flask-Mail is working."
        )
        mail.send(msg)
        return "✅ Gmail test email SENT", 200
    except Exception as e:
        current_app.logger.error(f"GMAIL TEST FAILED: {e}")
        return f"❌ Gmail test failed: {e}", 500




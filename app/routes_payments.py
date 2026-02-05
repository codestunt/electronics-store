
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
from datetime import datetime
import uuid

bp_pay = Blueprint("payments", __name__)  # registered with url_prefix="/pay"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def generate_order_id():
    return "EZ-" + uuid.uuid4().hex[:10].upper()


def _cart_to_line_items(cart):
    line_items = []
    for item in cart or []:
        qty = int(item.get("quantity", 1))
        price = float(item.get("price", 0))
        line_items.append({
            "quantity": qty,
            "price_data": {
                "currency": "aud",
                "unit_amount": int(price * 100),
                "product_data": {
                    "name": item.get("name", "Item")
                },
            },
        })
    return line_items


# -------------------------------------------------
# Stripe Checkout
# -------------------------------------------------

@bp_pay.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY")

    cart = session.get("cart", [])
    if not cart:
        return jsonify({"error": "Your cart is empty"}), 400

    data = request.get_json(silent=True) or {}
    email = session.get("user_email") or data.get("email")

    if email:
        session["user_email"] = email
        session.modified = True

    checkout_session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=_cart_to_line_items(cart),
        customer_email=email,
        success_url=current_app.config["BASE_URL"] + "/pay/success",
        cancel_url=current_app.config["BASE_URL"] + "/pay/cancel",

    )

    return jsonify({"id": checkout_session.id})


# -------------------------------------------------
# Stripe Success (FINAL LANDING PAGE)
# -------------------------------------------------

@bp_pay.route("/success")
def pay_success():
    cart = session.get("cart", [])

    items = []
    total = 0
    count = 0

    for item in cart:
        qty = int(item.get("quantity", 1))
        price = float(item.get("price", 0))
        subtotal = qty * price

        items.append({
            "name": item.get("name"),
            "qty": qty,
            "price": price,
            "subtotal": subtotal,
        })

        total += subtotal
        count += qty

    order_id = generate_order_id()

    session.update({
        "last_order_items": items,
        "last_order_total": total,
        "last_order_item_count": count,
        "last_order_ref": order_id,
        "cart": [],
    })
    session.modified = True

    flash("Payment successful. Thank you for your order!", "success")

    # ⚠️ IMPORTANT:
    # No email sending here.
    # No redirects after this.
    # Page MUST render immediately.

    return render_template(
        "order_complete.html",
        order_id=order_id,
        order_items=items,
        order_total=total,
        order_items_count=count,
        est_delivery_date=datetime.now().strftime("%d %b %Y"),
    )


# -------------------------------------------------
# Stripe Cancel
# -------------------------------------------------

@bp_pay.route("/cancel")
def pay_cancel():
    flash("Payment cancelled.", "error")
    return redirect(url_for("routes.cart"))

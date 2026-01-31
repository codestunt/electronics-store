from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, jsonify, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from app.extensions import mail, get_db_connection
from jinja2 import TemplateNotFound
from math import ceil
from datetime import datetime
import os
import re

# =========================================================
# Blueprint
# =========================================================
routes = Blueprint("routes", __name__)

# =========================================================
# Helpers
# =========================================================

def _send_form_email(subject: str, to_email: str, body: str, reply_to: str | None = None) -> None:
    """
    Send an email using Flask-Mail.
    """
    msg = Message(subject=subject, recipients=[to_email], body=body)
    if reply_to:
        msg.reply_to = reply_to
    mail.send(msg)


def _normalize_image_path(path: str | None) -> str:
    """Ensure image paths work with url_for('static', filename=...)."""
    if not path:
        return "images/placeholder.jpg"
    p = str(path).replace("\\", "/").lstrip("/")
    if p.startswith("static/"):
        p = p[len("static/"):]
    return p or "images/placeholder.jpg"


def _dict_rows(cursor):
    """
    psycopg2 RealDictCursor returns dict rows already.
    If yours returns tuples, you MUST update get_db_connection() to use RealDictCursor.
    """
    return cursor.fetchall()


# =========================================================
# Global template injections
# =========================================================
@routes.app_context_processor
def inject_cart_totals():
    cart = session.get("cart", [])
    total_quantity = sum(int(item.get("quantity", 1) or 1) for item in cart)
    return dict(total_cart_quantity=total_quantity)


@routes.app_context_processor
def inject_stripe_pk():
    # If you use Stripe on cart.html JS, keep this available globally too.
    return dict(stripe_pk=os.environ.get("STRIPE_PUBLISHABLE_KEY", ""))


# =========================================================
# Category config
# =========================================================
CATEGORY_MAP = {
    "tvs":        ("TVs",        "tv"),
    "audio":      ("Audio",      "audio"),
    "phones":     ("Phones",     "phone"),
    "projectors": ("Projectors", "projector"),
    "fridges":    ("Fridges",    "fridge"),
    "microwaves": ("Microwaves", "microwave"),
}

BANNER_MAP = {
    "tvs":        "images/banners/lg.jpg",
    "audio":      "images/banners/phoneHead.jpg",
    "phones":     "images/banners/galaxy.jpg",
    "projectors": "images/banners/projector.jpg",
    "fridges":    "images/banners/fridge.jpg",
    "microwaves": "images/banners/microwave.jpg",
}

SUBTITLE_MAP = {
    "tvs":        "Explore our best-in-class TVs.",
    "audio":      "Crisp sound for every room.",
    "phones":     "Discover the latest smartphones.",
    "projectors": "Big-screen experiences at home.",
    "fridges":    "Smart cooling, efficient living.",
    "microwaves": "Fast, even heating every time.",
}

HERO_BG_MAP = {
    "tvs": "#6F6F6F",
    "audio": "#ffffff",
    "phones": "#ffffff",
    "projectors": "#ffffff",
    "fridges": "#f6f6f6",
    "microwaves": "#ffffff",
}


def _get_products_by_tag(tag_like: str, page: int = 1, page_size: int = 12):
    offset = (max(page, 1) - 1) * page_size

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, name, price, image_path
            FROM products
            WHERE tag ILIKE %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (f"%{tag_like}%", page_size, offset),
        )
        rows = _dict_rows(cur)

        cur.execute(
            """
            SELECT COUNT(*) AS total
            FROM products
            WHERE tag ILIKE %s
            """,
            (f"%{tag_like}%",),
        )
        total_row = cur.fetchone()
        # total_row might be dict or tuple depending on cursor
        total = total_row["total"] if isinstance(total_row, dict) else total_row[0]

        for r in rows:
            if isinstance(r, dict):
                r["image_path"] = _normalize_image_path(r.get("image_path"))
        pages = (total + page_size - 1) // page_size

        return rows, total, pages
    finally:
        cur.close()
        conn.close()


@routes.route("/category/<slug>")
def category_page(slug):
    item = CATEGORY_MAP.get(slug.lower())
    if not item:
        return redirect(url_for("routes.home"))

    page_title, tag_like = item
    page = int(request.args.get("page", 1) or 1)

    products, total, pages = _get_products_by_tag(tag_like, page, page_size=24)

    banner_file = BANNER_MAP.get(slug.lower(), "images/banners/default.jpg")
    page_subtitle = SUBTITLE_MAP.get(slug.lower(), f"Explore our best-in-class {page_title}.")

    return render_template(
        "categories/grid.html",
        page_title=page_title,
        page_subtitle=page_subtitle,
        page_bg=banner_file,
        hero_bg_color=HERO_BG_MAP.get(slug.lower(), "#f5f5f5"),
        products=products,
        page=page,
        pages=pages,
    )


# =========================================================
# Newsletter
# =========================================================
@routes.route("/newsletter/join", methods=["POST"])
def newsletter_join():
    email = (request.form.get("email") or "").strip().lower()
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not email or "@" not in email:
        msg = "Please enter a valid email."
        if is_ajax:
            return jsonify(ok=False, message=msg), 400
        flash(msg, "signup_error")
        return redirect(request.referrer or url_for("routes.home"))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Postgres upsert
        cur.execute(
            """
            INSERT INTO newsletter_subscribers (email, status)
            VALUES (%s, 'subscribed')
            ON CONFLICT (email)
            DO UPDATE SET
                status='subscribed',
                updated_at = CURRENT_TIMESTAMP
            """,
            (email,),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    ok_msg = "Thank you for signing up!"
    if is_ajax:
        return jsonify(ok=True, message=ok_msg)
    flash(ok_msg, "signup_success")
    return redirect(request.referrer or url_for("routes.home"))


# =========================================================
# Auth
# =========================================================
@routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not full_name or not email or not password:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("routes.signup"))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            exists = cur.fetchone()
            if exists:
                flash("Email already exists!", "error")
                return redirect(url_for("routes.signup"))

            cur.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                (full_name, email, hashed_password),
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

        flash("Sign-up successful, please login!", "success")
        return redirect(url_for("routes.login"))

    return render_template("signup.html")


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, full_name, email, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
        finally:
            cur.close()
            conn.close()

        # user may be dict or tuple depending on cursor
        if isinstance(user, dict):
            ok = user and check_password_hash(user["password"], password)
            user_email = user["email"] if user else None
            user_name = user["full_name"] if user else None
        else:
            ok = user and check_password_hash(user[3], password)
            user_email = user[2] if user else None
            user_name = user[1] if user else None

        if ok:
            session.clear()
            session["loggedin"] = True
            session["user"] = user_email
            session["username"] = user_name
            session["email"] = user_email
            session["user_email"] = user_email  # used by your pay_complete() in payments blueprint
            flash("Login successful!", "success")
            return redirect(url_for("routes.dashboard"))

        flash("Invalid email or password!", "error")

    return render_template("login.html")


@routes.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please login to continue", "error")
        return redirect(url_for("routes.login"))
    return render_template("dashboard.html", user=session["user"])


@routes.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("routes.home"))


# =========================================================
# Home
# =========================================================
@routes.route("/")
def home():
    products = []

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, price, image_path, rating, review_count, tag
            FROM products
            ORDER BY id DESC
            LIMIT 100
        """)
        products = cur.fetchall()

    except Exception as e:
        current_app.logger.error(f"Home page DB error: {e}")

    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()

    for p in products:
        p["image_path"] = _normalize_image_path(p.get("image_path"))

    return render_template("index.html", bestsellers=products)


# =========================================================
# Cart
# =========================================================
@routes.route("/cart")
def cart():
    cart_items = session.get("cart", [])

    for item in cart_items:
        item["quantity"] = int(item.get("quantity", 1) or 1)

    total_items = sum(int(item["quantity"]) for item in cart_items)
    total_amount = sum(float(item.get("price", 0)) * int(item["quantity"]) for item in cart_items)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total_items,
        total_amount=total_amount,
        stripe_pk=os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
    )


@routes.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user" not in session:
        flash("Please sign in to add items to your cart.", "danger")
        return redirect(url_for("routes.login"))

    product_id = request.form.get("product_id")
    if not product_id:
        flash("Missing product id.", "danger")
        return redirect(url_for("routes.home"))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, price, image_path FROM products WHERE id = %s", (product_id,))
        product = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("routes.home"))

    if isinstance(product, dict):
        pid = product["id"]
        pname = product["name"]
        pprice = float(product["price"])
        pimage = _normalize_image_path(product.get("image_path"))
    else:
        pid = product[0]
        pname = product[1]
        pprice = float(product[2])
        pimage = _normalize_image_path(product[3])

    cart = session.get("cart", [])

    for item in cart:
        if str(item.get("id")) == str(pid):
            item["quantity"] = int(item.get("quantity", 1) or 1) + 1
            break
    else:
        cart.append({
            "id": pid,
            "name": pname,
            "price": pprice,
            "image_path": pimage,
            "quantity": 1,
        })

    session["cart"] = cart
    flash("Item added to cart!", "success")
    return redirect(url_for("routes.cart"))


@routes.route("/remove_from_cart/<product_id>", methods=["GET"])
def remove_from_cart(product_id):
    cart = session.get("cart", [])

    removed = False
    new_cart = []
    for it in cart:
        it_id = str(it.get("id", ""))
        it_sku = str(it.get("sku", ""))
        if not removed and (it_id == str(product_id) or it_sku == str(product_id)):
            removed = True
            continue
        new_cart.append(it)

    session["cart"] = new_cart
    flash("Item removed from cart.", "error")
    return redirect(url_for("routes.cart"))


@routes.route("/update_quantity", methods=["POST"])
def update_quantity():
    product_id = request.form.get("product_id")
    action = request.form.get("action")
    index_param = request.form.get("index")

    def norm(v):
        if v is None:
            return ""
        try:
            return str(int(v))
        except (TypeError, ValueError):
            return str(v)

    cart = session.get("cart", [])
    target_item = None

    # Prefer index if valid
    if index_param is not None and str(index_param).isdigit():
        i = int(index_param)
        if 0 <= i < len(cart):
            target_item = cart[i]

    # Otherwise match by id/sku
    if target_item is None and product_id is not None:
        pid = norm(product_id)
        for it in cart:
            if pid and (pid == norm(it.get("id")) or pid == norm(it.get("sku"))):
                target_item = it
                break

    if target_item is not None:
        current_qty = int(target_item.get("quantity", 1) or 1)
        if action == "increase":
            target_item["quantity"] = current_qty + 1
        elif action == "decrease" and current_qty > 1:
            target_item["quantity"] = current_qty - 1

    session["cart"] = cart
    return redirect(url_for("routes.cart"))


@routes.route("/checkout", methods=["POST"], endpoint="checkout")
def checkout():
    full_name = (request.form.get("full_name") or "").strip()
    email = (request.form.get("email") or "").strip()
    address = (request.form.get("address") or "").strip()
    payment_method = (request.form.get("payment_method") or "").strip()

    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("routes.cart"))

    if not payment_method:
        flash("Please select a payment method before placing your order.", "error")
        return redirect(url_for("routes.cart"))

    # Card payments should go through your payments blueprint (Stripe Checkout)
    if payment_method == "card":
        flash("Please use the card payment option on this page. If you see this message, something went wrong.", "error")
        return redirect(url_for("routes.cart"))

    # Non-card placeholder flow
    session["cart"] = []
    flash("Order placed successfully!", "success")
    return redirect(url_for("routes.home"))


# =========================================================
# Gift Card
# =========================================================
SALES_TEAM_EMAIL = "joemtaika@gmail.com"

@routes.route("/gift-card", methods=["GET", "POST"])
def gift_card():
    if request.method == "POST":
        design = request.form.get("design", "dark")
        amount = request.form.get("amount", "100")

        custom_amount = (request.form.get("custom_amount") or "").strip()
        final_amount = custom_amount if amount == "custom" else amount

        recipient_name = (request.form.get("recipient_name") or "").strip()
        recipient_email = (request.form.get("recipient_email") or "").strip()
        recipient_email_confirm = (request.form.get("recipient_email_confirm") or "").strip()

        from_name = (request.form.get("from_name") or "").strip()
        message = (request.form.get("message") or "").strip()

        if recipient_email.lower() != recipient_email_confirm.lower():
            flash("Recipient emails do not match.", "error")
            return redirect(url_for("routes.gift_card"))

        try:
            amt_num = int(float(final_amount))
            if amt_num < 5:
                flash("Custom amount must be at least $5.", "error")
                return redirect(url_for("routes.gift_card"))
        except ValueError:
            flash("Invalid gift card amount.", "error")
            return redirect(url_for("routes.gift_card"))

        cart = session.get("cart", [])
        cart.append({
            "id": f"gift-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": "Digital Gift Card",
            "price": float(amt_num),
            "image_path": "images/giftcard-dark.png",
            "quantity": 1,
            "type": "gift_card",
            "design": design,
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            "from_name": from_name,
            "gift_message": message,
        })
        session["cart"] = cart

        subject = f"New Gift Card Added To Cart — ${amt_num} ({design})"
        body = f"""NEW GIFT CARD — Added To Cart (ElectroZone)

TIME: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DESIGN: {design}
AMOUNT: ${amt_num}

RECIPIENT:
- Name: {recipient_name}
- Email: {recipient_email}

SENDER:
- Name: {from_name}

MESSAGE:
{message or "(no message)"}

ACTION:
Please prepare the voucher and send it to the recipient email above.
"""
        try:
            _send_form_email(subject=subject, to_email=SALES_TEAM_EMAIL, body=body, reply_to=recipient_email or None)
        except Exception as e:
            print("GIFT CARD EMAIL ERROR:", e)

        flash("Gift card added to cart!", "success")
        return redirect(url_for("routes.cart"))

    return render_template("gift_card.html")


# =========================================================
# Search (Render-safe)
# =========================================================
@routes.route("/search")
def search():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page", 1) or 1), 1)
    page_size = 12
    offset = (page - 1) * page_size

    if not q:
        flash("Please enter a search term.", "error")
        return redirect(url_for("routes.home"))

    like = f"%{q}%"

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM products
            WHERE name ILIKE %s OR review_summary ILIKE %s OR tag ILIKE %s
            """,
            (like, like, like),
        )
        total = cur.fetchone()[0] if not isinstance(cur.fetchone(), dict) else cur.fetchone()["count"]

        # Re-run because calling fetchone twice would consume it if dict cursor
        cur.execute(
            """
            SELECT COUNT(*)
            FROM products
            WHERE name ILIKE %s OR review_summary ILIKE %s OR tag ILIKE %s
            """,
            (like, like, like),
        )
        total = cur.fetchone()[0] if not isinstance(cur.fetchone(), dict) else cur.fetchone()["count"]

        cur.execute(
            """
            SELECT id, name, price, image_path, review_summary, tag
            FROM products
            WHERE name ILIKE %s OR review_summary ILIKE %s OR tag ILIKE %s
            ORDER BY name ASC
            LIMIT %s OFFSET %s
            """,
            (like, like, like, page_size, offset),
        )
        results = _dict_rows(cur)
    finally:
        cur.close()
        conn.close()

    # normalize images if dict rows
    for r in results:
        if isinstance(r, dict):
            r["image_path"] = _normalize_image_path(r.get("image_path"))

    pages = max(1, ceil(total / page_size))

    return render_template("search.html", q=q, results=results, total=total, page=page, pages=pages)


# =========================================================
# Product Finder (Render-safe)
# =========================================================
@routes.route("/product-finder", methods=["GET"])
def product_finder():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page", 1) or 1), 1)

    PER_PAGE = 16
    offset = (page - 1) * PER_PAGE

    where_sql = ""
    params = []

    if q:
        where_sql = """
            WHERE name ILIKE %s
               OR description ILIKE %s
               OR tag ILIKE %s
        """
        like = f"%{q}%"
        params = [like, like, like]

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM products")
        total_all = cur.fetchone()[0]

        cur.execute(f"SELECT COUNT(*) FROM products {where_sql}", params)
        total = cur.fetchone()[0]

        total_pages = max(1, ceil(total / PER_PAGE))

        cur.execute(
            f"""
            SELECT id, name, price, image_path, description,
                   COALESCE(stock_quantity, 0) AS stock_quantity
            FROM products
            {where_sql}
            ORDER BY name ASC
            LIMIT %s OFFSET %s
            """,
            params + [PER_PAGE, offset],
        )
        products = _dict_rows(cur)
    finally:
        cur.close()
        conn.close()

    for p in products:
        if isinstance(p, dict):
            p["image_path"] = _normalize_image_path(p.get("image_path"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        html = render_template(
            "_pf_results.html",
            products=products,
            page=page,
            total=total,
            total_pages=total_pages,
            q=q,
        )
        return jsonify({"html": html, "total": total, "total_all": total_all, "q": q})

    return render_template(
        "product_finder.html",
        products=products,
        page=page,
        total=total,
        total_all=total_all,
        total_pages=total_pages,
        q=q,
    )


# =========================================================
# Admin
# =========================================================
@routes.route("/admin")
def admin():
    try:
        return render_template("admin.html")
    except TemplateNotFound:
        return "Admin dashboard", 200


@routes.route("/admin/product/add", methods=["POST"], endpoint="add_product")
def add_product():
    name = (request.form.get("name") or "").strip()
    price_raw = (request.form.get("price") or "").strip()
    image_path = _normalize_image_path(request.form.get("image_path") or "")
    tag = (request.form.get("tag") or "").strip()
    review_summary = (request.form.get("review_summary") or "").strip()

    if not name or not price_raw:
        flash("Name and price are required.", "error")
        return redirect(url_for("routes.admin"))

    try:
        price = float(price_raw)
    except ValueError:
        flash("Invalid price format.", "error")
        return redirect(url_for("routes.admin"))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO products (name, price, image_path, tag, review_summary)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, price, image_path, tag, review_summary),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    flash("Product added successfully.", "success")
    return redirect(url_for("routes.admin"))


# =========================================================
# Account page
# =========================================================
@routes.route("/account")
def account():
    if "loggedin" in session:
        return render_template("account.html")
    return redirect(url_for("routes.login"))


# =========================================================
# Static / content pages
# =========================================================
@routes.route("/community")
def community():
    return render_template("community.html")


@routes.route("/corporate-sales", methods=["GET", "POST"])
def corporate_sales():
    if request.method == "POST":
        flash("Thanks! Our corporate team will get back to you shortly.", "success")
        return redirect(url_for("routes.corporate_sales"))
    return render_template("corporate_sales.html")


@routes.route("/help", endpoint="help", methods=["GET"])
def help_page():
    return render_template("help.html")


@routes.route("/about", methods=["GET"])
def about_electrozone():
    return render_template("about_electrozone.html")


@routes.route("/our-values")
def our_values():
    return render_template("our_values.html")


@routes.route("/terms-of-service")
def terms():
    return render_template("terms.html")


@routes.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")


@routes.route("/request-quote", methods=["GET", "POST"])
def request_quote():
    if request.method == "POST":
        flash("Thanks! Your quote request has been sent. We'll respond shortly.", "success")
        return redirect(url_for("routes.request_quote"))
    return render_template("request_quote.html")


@routes.route("/contact-sales", methods=["GET", "POST"])
def contact_sales():
    if request.method == "POST":
        flash("Thanks! Our sales team will contact you shortly.", "success")
        return redirect(url_for("routes.contact_sales"))
    return render_template("contact_sales.html")


@routes.route("/contact-support", methods=["GET", "POST"])
def contact_support():
    if request.method == "POST":
        flash("Thanks! Your support request has been received. We'll get back to you ASAP.", "success")
        return redirect(url_for("routes.contact_support"))
    return render_template("contact_support.html")


# =========================================================
# TEST EMAIL (keep if you want; you can remove later)
# =========================================================
@routes.route("/send-test-email")
def send_test_email():
    msg = Message(
        subject="ElectroZone Test Email",
        recipients=["test@example.com"],
        body="This is a test email from ElectroZone!"
    )
    mail.send(msg)
    return "<h2>Test email sent!</h2>"


# =========================================================
# FORM EMAIL HANDLERS (your 3 required routes)
# =========================================================

@routes.route("/forms/quote/send", methods=["POST"])
def ez_send_quote_form_to_gmail():
    company  = (request.form.get("company") or "").strip()
    contact  = (request.form.get("contact") or "").strip()
    email    = (request.form.get("email") or "").strip()
    phone    = (request.form.get("phone") or "").strip()
    category = (request.form.get("category") or "").strip()
    qty      = (request.form.get("qty") or "").strip()
    message  = (request.form.get("message") or "").strip()

    body = f"""NEW QUOTE REQUEST — ElectroZone

Company: {company}
Contact: {contact}
Email: {email}
Phone: {phone}
Category: {category}
Estimated Quantity: {qty}

Message:
{message}
"""
    try:
        _send_form_email(
            subject="New Quote Request — ElectroZone",
            to_email="joemtaika@gmail.com",
            body=body,
            reply_to=email or None
        )
        flash("Thanks! Your quote request has been sent.", "success")
    except Exception as e:
        print("QUOTE FORM EMAIL ERROR:", e)
        flash("Sorry — we couldn't send your request right now. Please try again.", "error")

    return redirect(url_for("routes.request_quote"))


@routes.route("/forms/sales/send", methods=["POST"])
def ez_send_sales_form_to_gmail():
    contact  = (request.form.get("contact") or "").strip()
    company  = (request.form.get("company") or "").strip()
    email    = (request.form.get("email") or "").strip()
    phone    = (request.form.get("phone") or "").strip()
    category = (request.form.get("category") or "").strip()
    qty      = (request.form.get("qty") or "").strip()
    message  = (request.form.get("message") or "").strip()

    body = f"""NEW SALES ENQUIRY — ElectroZone

Company: {company}
Contact: {contact}
Email: {email}
Phone: {phone}
Interest: {category}
Estimated Quantity: {qty}

Message:
{message}
"""
    try:
        _send_form_email(
            subject="New Sales Enquiry — ElectroZone",
            to_email="joemtaika@gmail.com",
            body=body,
            reply_to=email or None
        )
        flash("Thanks! Your message has been sent to Sales.", "success")
    except Exception as e:
        print("SALES FORM EMAIL ERROR:", e)
        flash("Sorry — we couldn't send your message right now. Please try again.", "error")

    return redirect(url_for("routes.contact_sales"))


@routes.route("/forms/support/send", methods=["POST"])
def ez_send_support_form_to_gmail():
    name    = (request.form.get("name") or request.form.get("contact") or "").strip()
    email   = (request.form.get("email") or "").strip()
    phone   = (request.form.get("phone") or "").strip()
    subject = (request.form.get("subject") or "Support Request").strip()
    message = (request.form.get("message") or "").strip()

    body = f"""NEW SUPPORT REQUEST — ElectroZone

Name: {name}
Email: {email}
Phone: {phone}
Subject: {subject}

Message:
{message}
"""
    try:
        _send_form_email(
            subject=f"Support: {subject} — ElectroZone",
            to_email="joemtaika@gmail.com",
            body=body,
            reply_to=email or None
        )
        flash("Thanks! Your support request has been sent.", "success")
    except Exception as e:
        print("SUPPORT FORM EMAIL ERROR:", e)
        flash("Sorry — we couldn't send your request right now. Please try again.", "error")

    return redirect(url_for("routes.contact_support"))

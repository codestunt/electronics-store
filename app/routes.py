from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from app.extensions import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re
from math import ceil
from decimal import Decimal
from app.extensions import mail
from flask_mail import Message   # 👈 add this
from datetime import datetime



def _send_form_email(subject: str, to_email: str, body: str, reply_to: str | None = None) -> None:
    """
    Send an email using Flask-Mail without touching any existing email feature.
    """
    msg = Message(
        subject=subject,
        recipients=[to_email],
        body=body
    )
    if reply_to:
        msg.reply_to = reply_to

    mail.send(msg)


# ✅ Define the blueprint BEFORE using @routes.route
routes = Blueprint('routes', __name__)

# Make cart total available to every template (layout, category pages, etc.)
@routes.app_context_processor
def inject_cart_totals():
    cart = session.get("cart", [])
    total_quantity = sum(int(item.get("quantity", 1)) for item in cart)
    return dict(total_cart_quantity=total_quantity)

# Map each category page to the tag stored in the DB
CATEGORY_MAP = {
    "tvs":        ("TVs",        "tv"),
    "audio":      ("Audio",      "audio"),
    "phones":     ("Phones",     "phone"),
    "projectors": ("Projectors", "projector"),
    "fridges":    ("Fridges",    "fridge"),
    "microwaves": ("Microwaves", "microwave"),
}

# Map each category slug to a banner image in /static/images/banners
BANNER_MAP = {
    "tvs":        "images/banners/lg.jpg",
    "audio":      "images/banners/phoneHead.jpg",
    "phones":     "images/banners/galaxy.jpg",
    "projectors": "images/banners/projector.jpg",
    "fridges":    "images/banners/fridge.jpg",
    "microwaves": "images/banners/microwave.jpg",
}

# Put this near BANNER_MAP
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


TEXT_COLOR_MAP = {
    "tvs":        "#111111",
    "audio":      "#111111",
    "phones":     "#111111",
    "projectors": "#111111",
    "fridges":    "#111111",
    "microwaves": "#111111",
}

@routes.route('/category/<slug>')
def category_page(slug):
    item = CATEGORY_MAP.get(slug.lower())
    if not item:
        return redirect(url_for('routes.home'))

    page_title, tag_like = item
    page = int(request.args.get('page', 1) or 1)

    products, total, pages = _get_products_by_tag(tag_like, page, page_size=24)

    banner_file   = BANNER_MAP.get(slug.lower(), "images/banners/default.jpg")
    page_subtitle = SUBTITLE_MAP.get(slug.lower(), f"Explore our best-in-class {page_title}.")

    return render_template(
    'categories/grid.html',
    page_title=page_title,
    page_subtitle=page_subtitle,
    page_bg=banner_file,
    hero_bg_color=HERO_BG_MAP.get(slug.lower(), "#f5f5f5"),
    products=products,
    page=page,
    pages=pages,
)


def _normalize_image_path(path: str | None) -> str:
    """Make sure the path is relative to /static and give a placeholder if empty."""
    if not path:
        return "images/placeholder.jpg"
    p = path.replace("\\", "/").lstrip("/")
    if p.startswith("static/"):
        p = p[len("static/"):]
    return p or "images/placeholder.jpg"

def _get_products_by_tag(tag_like: str, page: int = 1, page_size: int = 12):
    offset = (max(page, 1) - 1) * page_size
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # data
        cur.execute("""
            SELECT id, name, price, image_path
            FROM products
            WHERE tag LIKE %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """, (f"%{tag_like}%", page_size, offset))
        rows = cur.fetchall()

        # total
        cur.execute("""
            SELECT COUNT(*) AS total
            FROM products
            WHERE tag LIKE %s
        """, (f"%{tag_like}%",))
        total = cur.fetchone()["total"]

        # normalize image paths
        for r in rows:
            r["image_path"] = _normalize_image_path(r.get("image_path"))

        pages = (total + page_size - 1) // page_size
        return rows, total, pages
    finally:
        cur.close()

def _save_newsletter_email(raw_email: str) -> bool:
    email = (raw_email or "").strip().lower()
    if not email or "@" not in email:
        return False

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute(
            """
            INSERT INTO newsletter_subscribers (email)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP
            """,
            (email,)
        )
        mysql.connection.commit()
        return True
    finally:
        cur.close()

users = []  # Not used in session-based app

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email already exists!', 'error')
        else:
            cursor.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                (full_name, email, hashed_password)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Sign-up successful, please login!', 'success')
            return redirect(url_for('routes.login'))

    return render_template('signup.html')

from datetime import datetime  # ✅ add near your imports

SALES_TEAM_EMAIL = "joemtaika@gmail.com"

@routes.route("/gift-card", methods=["GET", "POST"])
def gift_card():
    if request.method == "POST":
        design = request.form.get("design", "dark")
        amount = request.form.get("amount", "100")

        custom_amount = (request.form.get("custom_amount") or "").strip()
        final_amount = custom_amount if amount == "custom" else amount

        recipient_name  = (request.form.get("recipient_name") or "").strip()
        recipient_email = (request.form.get("recipient_email") or "").strip()
        recipient_email_confirm = (request.form.get("recipient_email_confirm") or "").strip()

        from_name = (request.form.get("from_name") or "").strip()
        message   = (request.form.get("message") or "").strip()

        # Validate emails
        if recipient_email.lower() != recipient_email_confirm.lower():
            flash("Recipient emails do not match.", "error")
            return redirect(url_for("routes.gift_card"))

        # Validate amount
        try:
            amt_num = int(float(final_amount))
            if amt_num < 5:
                flash("Custom amount must be at least $5.", "error")
                return redirect(url_for("routes.gift_card"))
        except ValueError:
            flash("Invalid gift card amount.", "error")
            return redirect(url_for("routes.gift_card"))

        # ✅ 1) ADD TO CART using the SAME amt_num
        cart = session.get("cart", [])
        cart.append({
            "id": f"gift-{datetime.now().strftime('%Y%m%d%H%M%S')}",  # unique id
            "name": "Digital Gift Card",
            "price": float(amt_num),   # ✅ THIS is what your cart displays
            "image_path": "images/giftcard-dark.png",  # or whatever you want shown in cart
            "quantity": 1,

            # extra details (optional but useful later)
            "type": "gift_card",
            "design": design,
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            "from_name": from_name,
            "gift_message": message
        })
        session["cart"] = cart

        # ✅ 2) SEND EMAIL using the SAME amt_num
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
            _send_form_email(
                subject=subject,
                to_email=SALES_TEAM_EMAIL,
                body=body,
                reply_to=recipient_email or None
            )
        except Exception as e:
            print("GIFT CARD EMAIL ERROR:", e)

        flash("Gift card added to cart!", "success")
        return redirect(url_for("routes.cart"))

    return render_template("gift_card.html")
    

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            # Optional: clear old session to avoid stale data
            session.clear()

            session['loggedin'] = True
            session['user'] = user['email']          # legacy key (if other code uses it)
            session['username'] = user['full_name']
            session['email'] = user['email']         # legacy key (if other code uses it)

            # 🔥 This is the important one for receipts:
            session['user_email'] = user['email']    # used by pay_complete()

            flash('Login successful!', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@routes.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login to continue', 'error')
        return redirect(url_for('routes.login'))
    return render_template('dashboard.html', user=session['user'])

@routes.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('routes.home'))

@routes.route('/')
def home():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, name, price, image_path, rating, review_count, tag FROM products ORDER BY id DESC LIMIT 100")
    products = cur.fetchall()
    cur.close()
    return render_template('index.html', bestsellers=products)

from flask import render_template, session, current_app

@routes.route('/cart')
def cart():
    cart = session.get('cart', [])

    # Make sure quantity is always an int ≥ 1
    for item in cart:
        item['quantity'] = int(item.get('quantity', 1) or 1)

    total_items = sum(item['quantity'] for item in cart)
    total_amount = sum(item['price'] * item['quantity'] for item in cart)

    return render_template(
        'cart.html',
        cart_items=cart,
        total=total_items,
        total_amount=total_amount,
        stripe_pk=current_app.config["STRIPE_PUBLISHABLE_KEY"]  # 👈 used in JS
    )


@routes.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        flash('Please sign in to add items to your cart.', 'danger')
        return redirect(url_for('routes.login'))

    product_id = request.form.get('product_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if product:
        if 'cart' not in session:
            session['cart'] = []

        cart = session['cart']
        for item in cart:
            if item['id'] == product['id']:
                item['quantity'] += 1
                break
        else:
            cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': float(product['price']),
                'image_path': product['image_path'],
                'quantity': 1
            })

        session['cart'] = cart
        flash('Item added to cart!', 'success')
    else:
        flash('Product not found.', 'danger')

    return redirect(url_for('routes.cart'))

@routes.route('/checkout', methods=['POST'], endpoint='checkout')
def checkout():
    full_name      = (request.form.get('full_name') or '').strip()
    email          = (request.form.get('email') or '').strip()
    address        = (request.form.get('address') or '').strip()
    payment_method = (request.form.get('payment_method') or '').strip()

    cart = session.get('cart', [])
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('routes.cart'))

    # Require a payment method
    if not payment_method:
        flash('Please select a payment method before placing your order.', 'error')
        return redirect(url_for('routes.cart'))

    # Card payments must go through Stripe (JS + /pay/create-checkout-session)
    if payment_method == 'card':
        flash('Please use the card payment option on this page. If you see this message, something went wrong.', 'error')
        return redirect(url_for('routes.cart'))

    # Here you can handle non-card options (e.g. Cash on Delivery, Bank Transfer)
    # For now we just mark as “success”.
    # TODO: store order in DB etc.
    print("--- NON-card checkout ---")
    print("Name:", full_name)
    print("Email:", email)
    print("Address:", address)
    print("Payment:", payment_method)
    print("Cart:", cart)

    session['cart'] = []
    flash('Order placed successfully!', 'success')
    return redirect(url_for('routes.home'))


@routes.route('/remove_from_cart/<product_id>', methods=['GET'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])

    # keep the first match removed; leave others as-is
    removed = False
    new_cart = []
    for it in cart:
        # try to match by id or sku, normalize to str
        it_id = str(it.get('id', ''))
        it_sku = str(it.get('sku', ''))
        if not removed and (it_id == str(product_id) or it_sku == str(product_id)):
            removed = True
            continue
        new_cart.append(it)

    session['cart'] = new_cart
    flash('Item removed from cart.', 'error')  # shows red banner per your setup
    return redirect(url_for('routes.cart'))

# ✅ Update Quantity Route
@routes.route('/update_quantity', methods=['POST'])
def update_quantity():
    # Accept string or numeric IDs; do NOT cast to int
    product_id = request.form.get('product_id')           # e.g., "42" or "gift-1"
    action      = request.form.get('action')              # "increase" | "decrease"
    index_param = request.form.get('index')               # optional loop.index0 from template

    def norm(v):
        """Normalize any id/sku to a comparable string."""
        if v is None:
            return ""
        try:
            # if it's numeric-like, compare as its integer string ("007" -> "7")
            return str(int(v))
        except (TypeError, ValueError):
            return str(v)

    if 'cart' in session:
        cart = session['cart']
        target_item = None

        # 1) Prefer index if provided & valid (works for any id type and duplicates)
        if index_param is not None and str(index_param).isdigit():
            i = int(index_param)
            if 0 <= i < len(cart):
                target_item = cart[i]

        # 2) Otherwise find by id or sku (string-safe match)
        if target_item is None and product_id is not None:
            pid = norm(product_id)
            for it in cart:
                it_id  = norm(it.get('id'))
                it_sku = norm(it.get('sku'))
                if pid and (pid == it_id or pid == it_sku):
                    target_item = it
                    break

        # Apply your original increase/decrease rules (unchanged)
        if target_item is not None:
            current_qty = int(target_item.get('quantity', 1))
            if action == 'increase':
                target_item['quantity'] = current_qty + 1
            elif action == 'decrease' and current_qty > 1:
                target_item['quantity'] = current_qty - 1

        session['cart'] = cart

    return redirect(url_for('routes.cart'))

@routes.route('/account')
def account():
    if 'loggedin' in session:
        return render_template('account.html')
    return redirect(url_for('routes.login'))

@routes.route('/search')
def search():
    q = (request.args.get('q') or '').strip()
    page = max(int(request.args.get('page', 1) or 1), 1)
    page_size = 12
    offset = (page - 1) * page_size

    if not q:
        flash('Please enter a search term.', 'error')
        return redirect(url_for('routes.home'))

    match_cols = "MATCH(name, review_summary, tag)"
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # ---------- Try NATURAL LANGUAGE (best relevance) ----------
    count_sql_nat = f"SELECT COUNT(*) AS total FROM products WHERE {match_cols} AGAINST (%s IN NATURAL LANGUAGE MODE)"
    cur.execute(count_sql_nat, (q,))
    total = cur.fetchone()['total']

    if total > 0:
        data_sql_nat = (
            f"SELECT id, name, price, image_path, review_summary, tag, "
            f"{match_cols} AGAINST (%s IN NATURAL LANGUAGE MODE) AS score "
            f"FROM products "
            f"WHERE {match_cols} AGAINST (%s IN NATURAL LANGUAGE MODE) "
            f"ORDER BY score DESC "
            f"LIMIT %s OFFSET %s"
        )
        cur.execute(data_sql_nat, (q, q, page_size, offset))
        results = cur.fetchall()
        cur.close()
        pages = ceil(total / page_size)
        return render_template('search.html', q=q, results=results, total=total, page=page, pages=pages)

    # ---------- If nothing, try BOOLEAN MODE with wildcards (handles partials) ----------
    # Split words & quoted phrases; require each term (+) and allow prefix matching (*)
    terms = [t.strip('"') for t in re.findall(r'"[^"]+"|\S+', q)]
    boolean_query_terms = []
    for t in terms:
        if len(t) >= 3:                      # FULLTEXT ignores very short words by default
            boolean_query_terms.append(f'+{t}*')
    boolean_query = " ".join(boolean_query_terms) or q  # fallback to raw q if everything is short

    count_sql_bool = f"SELECT COUNT(*) AS total FROM products WHERE {match_cols} AGAINST (%s IN BOOLEAN MODE)"
    cur.execute(count_sql_bool, (boolean_query,))
    total = cur.fetchone()['total']

    if total > 0:
        data_sql_bool = (
            f"SELECT id, name, price, image_path, review_summary, tag, "
            f"{match_cols} AGAINST (%s IN BOOLEAN MODE) AS score "
            f"FROM products "
            f"WHERE {match_cols} AGAINST (%s IN BOOLEAN MODE) "
            f"ORDER BY score DESC "
            f"LIMIT %s OFFSET %s"
        )
        cur.execute(data_sql_bool, (boolean_query, boolean_query, page_size, offset))
        results = cur.fetchall()
        cur.close()
        pages = ceil(total / page_size)
        return render_template('search.html', q=q, results=results, total=total, page=page, pages=pages)

    # ---------- Last fallback: LIKE (for very short terms like "4K", "TV") ----------
    like_terms = [t for t in terms if t]
    where_parts, params = [], []
    for t in like_terms:
        like = f"%{t}%"
        where_parts.append("(name LIKE %s OR review_summary LIKE %s OR tag LIKE %s)")
        params.extend([like, like, like])
    where_sql = " WHERE " + " AND ".join(where_parts) if where_parts else ""

    cur.execute(f"SELECT COUNT(*) AS total FROM products{where_sql}", params)
    total = cur.fetchone()['total']

    data_sql_like = (
        f"SELECT id, name, price, image_path, review_summary, tag "
        f"FROM products{where_sql} "
        f"ORDER BY id DESC LIMIT %s OFFSET %s"
    )
    cur.execute(data_sql_like, params + [page_size, offset])
    results = cur.fetchall()
    cur.close()
    pages = ceil(total / page_size) if total else 1
    return render_template('search.html', q=q, results=results, total=total, page=page, pages=pages)

from jinja2 import TemplateNotFound  # add near your imports

@routes.route('/admin')
def admin():
    """
    Minimal, always-valid admin endpoint.
    Tries to render admin.html; falls back to plain text so Flask always
    gets a valid Response and never 500s due to None.
    """
    try:
        return render_template('admin.html')
    except TemplateNotFound:
        return "Admin dashboard", 200

# ✅ Create product from the Admin page
@routes.route('/admin/product/add', methods=['POST'], endpoint='add_product')
def add_product():
    name = (request.form.get('name') or '').strip()
    price_raw = (request.form.get('price') or '').strip()
    image_path = _normalize_image_path(request.form.get('image_path') or '')
    tag = (request.form.get('tag') or '').strip()
    review_summary = (request.form.get('review_summary') or '').strip()

    # validation
    if not name or not price_raw:
        flash('Name and price are required.', 'error')
        return redirect(url_for('routes.admin'))

    try:
        price = float(price_raw)
    except ValueError:
        flash('Invalid price format.', 'error')
        return redirect(url_for('routes.admin'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute(
            """
            INSERT INTO products (name, price, image_path, tag, review_summary)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, price, image_path, tag, review_summary)
        )
        mysql.connection.commit()
        flash('Product added successfully.', 'success')
    finally:
        cur.close()

    return redirect(url_for('routes.admin'))

@routes.route('/newsletter/join', methods=['POST'])
def newsletter_join():
    email = (request.form.get('email') or '').strip().lower()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not email or '@' not in email:
        msg = "Please enter a valid email."
        if is_ajax:
            return jsonify(ok=False, message=msg), 400
        flash(msg, "signup_error")
        return redirect(request.referrer or url_for('routes.index'))

    # ✅ Save email into DB
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute("""
            INSERT INTO newsletter_subscribers (email, status)
            VALUES (%s, 'subscribed')
            ON DUPLICATE KEY UPDATE
                status='subscribed',
                updated_at = CURRENT_TIMESTAMP
        """, (email,))
        mysql.connection.commit()
    finally:
        cur.close()

    ok_msg = "Thank you for signing up!"
    if is_ajax:
        return jsonify(ok=True, message=ok_msg)
    flash(ok_msg, "signup_success")
    return redirect(request.referrer or url_for('routes.home'))

@routes.route("/product-finder", methods=["GET"])
def product_finder():
    q = (request.args.get("q") or "").strip()
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    PER_PAGE = 16
    offset = (page - 1) * PER_PAGE

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Build WHERE + params safely
    where = ""
    params = []
    if q:
        where = """
            WHERE
                p.name LIKE %s OR
                p.description LIKE %s OR
                p.category LIKE %s
        """
        like = f"%{q}%"
        params.extend([like, like, like])

    # Total count
    # ✅ Total number of ALL products (no filters)
    cur.execute("SELECT COUNT(*) AS c FROM products")
    total_all = cur.fetchone()["c"]

    cur.execute(f"SELECT COUNT(*) AS c FROM products p {where}", params)
    total = cur.fetchone()["c"] if cur.rowcount else 0

    total_pages = max(1, ceil(total / PER_PAGE))

    # Page of results
    cur.execute(
        f"""
        SELECT
          p.id, p.name, p.price, p.image_path, p.description,
          COALESCE(p.stock_quantity, 0) AS stock_quantity
        FROM products p
        {where}
        ORDER BY p.name ASC
        LIMIT %s OFFSET %s
        """,
        params + [PER_PAGE, offset]
    )
    products = cur.fetchall()

    # Render whole page or partial for AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        html = render_template(
            "_pf_results.html",
            products=products,
            page=page,
            total=total,
            total_pages=total_pages,
            q=q,
        )
        return jsonify({
        "html": html,
        "total": total,
        "total_all": total_all,
        "q": q
})


    return render_template(
    "product_finder.html",
    products=products,
    page=page,
    total=total,
    total_all=total_all,
    total_pages=total_pages,
    q=q,
)


@routes.route("/community")
def community():
    # If you later want to pull real threads/reviews from DB, pass data here.
    return render_template("community.html")

# in routes.py
@routes.route("/corporate-sales", methods=["GET", "POST"])
def corporate_sales():
  if request.method == "POST":
      data = {
          "company": request.form.get("company","").strip(),
          "contact": request.form.get("contact","").strip(),
          "email":   request.form.get("email","").strip(),
          "phone":   request.form.get("phone","").strip(),
          "category":request.form.get("category","").strip(),
          "qty":     request.form.get("qty","").strip(),
          "message": request.form.get("message","").strip(),
      }
      # TODO: save to DB / send email
      flash("Thanks! Our corporate team will get back to you shortly.", "success")
      return redirect(url_for("routes.corporate_sales"))
  return render_template("corporate_sales.html")

@routes.route("/help", endpoint="help", methods=["GET"])
def help_page():
    return render_template("help.html")

# routes.py (add anywhere near your other page routes)
@routes.route("/about", methods=["GET"])
def about_electrozone():
    return render_template("about_electrozone.html")

# --- Our Values page ---
@routes.route("/our-values")
def our_values():
    return render_template("our_values.html")

# routes.py (add alongside inject_cart_totals)
import os

@routes.app_context_processor
def inject_stripe_pk():
    return dict(stripe_pk=os.environ.get("STRIPE_PUBLISHABLE_KEY", ""))


test_email_bp = Blueprint('test_email', __name__)

@routes.route("/send-test-email")
def send_test_email():
    msg = Message(
        subject="ElectroZone Test Email",
        recipients=["test@example.com"],  # any address; Mailtrap will catch it
        body="This is a test email from ElectroZone using Mailtrap!"
    )
    mail.send(msg)
    return "<h2>Test email sent!</h2>"



@routes.route("/terms-of-service")
def terms():
    return render_template("terms.html")


@routes.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")

# --- Request a Quote page ---
@routes.route("/request-quote", methods=["GET", "POST"])
def request_quote():
    if request.method == "POST":
        # later you can save to DB or email it
        flash("Thanks! Your quote request has been sent. We'll respond shortly.", "success")
        return redirect(url_for("routes.request_quote"))
    return render_template("request_quote.html")


# --- Contact Sales page (new) ---
@routes.route("/contact-sales", methods=["GET", "POST"])
def contact_sales():
    if request.method == "POST":
        flash("Thanks! Our sales team will contact you shortly.", "success")
        return redirect(url_for("routes.contact_sales"))
    return render_template("contact_sales.html")



# --- Contact Support page ---
@routes.route("/contact-support", methods=["GET", "POST"])
def contact_support():
    if request.method == "POST":
        flash("Thanks! Your support request has been received. We'll get back to you ASAP.", "success")
        return redirect(url_for("routes.contact_support"))
    return render_template("contact_support.html")


# =========================================================
# NEW: Email handlers (unique names + unique endpoints)
# These do NOT collide with existing request_quote/contact_sales/contact_support
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

    return redirect(url_for("routes.request_quote"))  # keep your existing page route


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

    return redirect(url_for("routes.contact_sales"))  # keep your existing page route


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

    return redirect(url_for("routes.contact_support"))  # keep your existing page route

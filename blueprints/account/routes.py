from decimal import Decimal

from flask import (
    render_template, request, redirect,
    url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

from . import account_bp
from database import db
from models import User, Product, Order, OrderItem, Transaction
from forms import CheckoutForm


# --- HELPERS ---

def require_login():
    """Return True if logged in, otherwise redirect to login."""
    if not session.get("user_id"):
        return False
    return True


def get_cart():
    """Return cart from session as dict {product_id_str: quantity_int}."""
    return session.get("cart", {})


def save_cart(cart):
    """Save cart back into session."""
    session["cart"] = cart
    session.modified = True


# --- PAGE: My Account ---

@account_bp.route("/my-account", methods=["GET", "POST"])
def my_account():

    if not require_login():
        return redirect(url_for("auth.register_page"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_username":
            new_username = (request.form.get("new_username") or "").strip()
            if new_username:
                user.username = new_username
                session["username"] = new_username
                db.session.commit()
                flash("Username updated!", "success")

        elif action == "update_password":
            new_password = request.form.get("new_password")
            if new_password:
                user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash("Password updated!", "success")

        elif action == "update_email":
            new_email = (request.form.get("new_email") or "").strip().lower()
            if new_email:
                user.email = new_email
                session["email"] = new_email
                db.session.commit()
                flash("Email updated!", "success")

        elif action == "update_address":
            new_address = (request.form.get("shipping_address") or "").strip()
            user.shipping_address = new_address or None
            db.session.commit()
            flash("Shipping address updated.", "success")

        elif action == "update_settings":
            flash("Settings saved.", "success")

        return redirect(url_for("account.my_account"))

    return render_template("account/my_account.html", user=user)



# ------------------------------------------------
# CART ROUTES
# ------------------------------------------------

@account_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    if not require_login():
        flash("Please sign in to add items to your cart.", "error")
        return redirect(url_for("auth.register_page"))

    product = Product.query.get_or_404(product_id)

    if product.status != "active" or product.stock_quantity <= 0:
        flash("This product is not currently available.", "error")
        return redirect(url_for("shop.product_page", product_id=product_id))

    cart = get_cart()
    key = str(product_id)
    current_qty = int(cart.get(key, 0))

    if current_qty + 1 > product.stock_quantity:
        flash("Not enough stock available.", "error")
    else:
        cart[key] = current_qty + 1
        save_cart(cart)
        flash("Product added to cart.", "success")

    return redirect(url_for("shop.product_page", product_id=product_id))



@account_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    key = str(product_id)
    if key in cart:
        del cart[key]
        save_cart(cart)
        flash("Item removed from cart.", "success")
    return redirect(url_for("account.view_cart"))



@account_bp.route("/cart/clear", methods=["POST"])
def clear_cart():
    if "cart" in session:
        session.pop("cart")
        flash("Cart cleared.", "success")
    return redirect(url_for("account.view_cart"))



@account_bp.route("/cart")
def view_cart():
    cart = get_cart()
    if not cart:
        return render_template("account/cart.html", cart_items=[], cart_total=Decimal("0.00"))

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.product_id.in_(product_ids)).all()

    items = []
    total = Decimal("0.00")

    for product in products:
        qty = int(cart.get(str(product.product_id), 0))
        if qty <= 0:
            continue

        line_total = product.price * qty
        total += line_total

        items.append({
            "product": product,
            "quantity": qty,
            "line_total": line_total,
        })

    return render_template("account/cart.html", cart_items=items, cart_total=total)



# ------------------------------------------------
# CHECKOUT + ORDER CREATION (FIXED)
# ------------------------------------------------

@account_bp.route("/checkout", methods=["GET", "POST"])
def checkout():

    if not require_login():
        return redirect(url_for("auth.register_page"))

    cart = get_cart()
    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for("account.view_cart"))

    user = User.query.get(session["user_id"])
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.product_id.in_(product_ids)).all()
    product_map = {p.product_id: p for p in products}

    form = CheckoutForm()

    # POST — Process checkout
    if form.validate_on_submit():

        shipping_address = f"""
{form.full_name.data}
{form.address.data}
{form.city.data}
{form.postcode.data}
{form.country.data}
""".strip()

        created_order_ids = []

        for pid_str, qty in cart.items():
            qty = int(qty)
            if qty <= 0:
                continue

            product = product_map.get(int(pid_str))
            if not product:
                continue

            if qty > product.stock_quantity:
                flash(f"Not enough stock for {product.name}.", "error")
                return redirect(url_for("account.view_cart"))

            line_total = product.price * qty

            order = Order(
                buyer_id=user.user_id,
                seller_id=product.seller_id,
                total_amount=line_total,
                payment_status="completed",  # always succeed
                shipping_address=shipping_address,
                delivery_status="processing",
            )
            db.session.add(order)
            db.session.flush()

            order_item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=qty,
                unit_price=product.price,
                subtotal=line_total,
            )
            db.session.add(order_item)

            product.stock_quantity -= qty
            if product.stock_quantity <= 0:
                product.status = "sold_out"

            tx = Transaction(
                user_id=user.user_id,
                related_order_id=order.order_id,
                transaction_type="purchase",
                amount=line_total,
            )
            db.session.add(tx)

            created_order_ids.append(order.order_id)

        db.session.commit()

        session.pop("cart", None)
        session["last_order_ids"] = created_order_ids

        return redirect(url_for("account.order_confirmation"))

    # GET — Show checkout page
    items = []
    total = Decimal("0.00")

    for pid_str, qty in cart.items():
        product = product_map.get(int(pid_str))
        if not product:
            continue

        qty = int(qty)
        line_total = product.price * qty
        total += line_total

        items.append({
            "product": product,
            "quantity": qty,
            "line_total": line_total,
        })

    return render_template(
        "account/checkout.html",
        cart_items=items,
        cart_total=total,
        user=user,
        form=form
    )



@account_bp.route("/order-confirmation")
def order_confirmation():

    if not require_login():
        return redirect(url_for("auth.register_page"))

    order_ids = session.get("last_order_ids")
    if not order_ids:
        return redirect(url_for("account.order_history"))

    orders = Order.query.filter(Order.order_id.in_(order_ids)).all()

    session.pop("last_order_ids", None)

    return render_template("account/order_confirmation.html", orders=orders)



@account_bp.route("/order-history")
def order_history():

    if not require_login():
        return redirect(url_for("auth.register_page"))

    user_id = session["user_id"]

    orders = (
        Order.query
        .filter_by(buyer_id=user_id)
        .order_by(Order.order_date.desc())
        .all()
    )

    return render_template("account/order_history.html", orders=orders)

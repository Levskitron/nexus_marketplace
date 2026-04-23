from decimal import Decimal
import os
import json

from flask import (
    render_template, request, redirect,
    url_for, session, flash, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

from . import account_bp
from database import db
from models import User, Product, Order, OrderItem, Transaction, CreditTopup, StripeCheckoutSession
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


def _stripe_configured() -> bool:
    return bool(os.getenv("STRIPE_SECRET_KEY"))


def _stripe_set_api_key():
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def _stripe_webhook_secret() -> str | None:
    return os.getenv("STRIPE_WEBHOOK_SECRET") or None


def _fulfill_paid_checkout(stripe_session_id: str, *, user_id: int | None = None) -> list[int]:
    """
    Create orders for a paid Stripe Checkout Session exactly once.
    Returns list of created order IDs (may be empty).
    """
    record = StripeCheckoutSession.query.get(stripe_session_id)
    if not record:
        return []

    if user_id is not None and record.user_id != user_id:
        return []

    if record.fulfilled:
        try:
            return json.loads(record.order_ids_json or "[]")
        except Exception:
            return []

    if record.payment_status != "paid":
        return []

    try:
        cart = json.loads(record.cart_json or "{}")
    except Exception:
        cart = {}

    if not isinstance(cart, dict) or not cart:
        return []

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.product_id.in_(product_ids)).all()
    product_map = {p.product_id: p for p in products}
    user = User.query.get(record.user_id)

    created_order_ids: list[int] = []

    for pid_str, qty in cart.items():
        qty = int(qty)
        if qty <= 0:
            continue

        product = product_map.get(int(pid_str))
        if not product:
            continue

        if product.status != "active" or qty > product.stock_quantity:
            continue

        line_total = product.price * qty

        order = Order(
            buyer_id=user.user_id,
            seller_id=product.seller_id,
            total_amount=line_total,
            payment_status="completed",
            shipping_address=record.shipping_address,
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

    record.fulfilled = True
    record.order_ids_json = json.dumps(created_order_ids)
    db.session.commit()

    return created_order_ids


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

        elif action == "add_credits":
            try:
                amount = Decimal(request.form.get("topup_amount") or "0")
            except Exception:
                amount = Decimal("0")
            if amount > 0 and amount <= Decimal("99999.99"):
                user.credits_balance += amount
                topup = CreditTopup(
                    user_id=user.user_id,
                    topup_amount=amount,
                    payment_reference=request.form.get("payment_reference") or None,
                )
                db.session.add(topup)
                tx = Transaction(
                    user_id=user.user_id,
                    transaction_type="credit_topup",
                    amount=amount,
                )
                db.session.add(tx)
                db.session.commit()
                flash(f"Added £{amount:.2f} to your account. New balance: £{user.credits_balance:.2f}", "success")
            else:
                flash("Please enter a valid amount (e.g. 10.00).", "error")

        elif action == "become_seller":
            if user.role == "buyer":
                user.role = "seller"
                db.session.commit()
                flash("You are now a seller. You can add products from the Seller Dashboard.", "success")
            else:
                flash("Your account already has seller access.", "error")

        elif action == "remove_seller_role":
            if user.role == "seller":
                user.role = "buyer"
                db.session.commit()
                flash("Seller role removed. Your listings are unchanged but you can no longer add new products.", "success")
            else:
                flash("You do not have the seller role.", "error")

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

    back = request.referrer if request.referrer and request.host in request.referrer else None
    return redirect(back or url_for("shop.product_page", product_id=product_id))


@account_bp.route("/cart/decrease/<int:product_id>", methods=["POST"])
def decrease_cart(product_id):
    """Decrease quantity by 1; remove item if 0."""
    cart = get_cart()
    key = str(product_id)
    if key in cart:
        cart[key] = max(0, int(cart[key]) - 1)
        if cart[key] == 0:
            del cart[key]
        save_cart(cart)
    back = request.referrer if request.referrer and request.host in request.referrer else url_for("account.view_cart")
    return redirect(back)


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

        if not _stripe_configured():
            flash("Stripe is not configured. Add STRIPE_SECRET_KEY to your environment.", "error")
            return redirect(url_for("account.checkout"))

        shipping_address = f"""
{form.full_name.data}
{form.address.data}
{form.city.data}
{form.postcode.data}
{form.country.data}
""".strip()

        # Validate stock now (before sending user to Stripe)
        for pid_str, qty in cart.items():
            qty = int(qty)
            if qty <= 0:
                continue
            product = product_map.get(int(pid_str))
            if not product:
                continue
            if product.status != "active" or qty > product.stock_quantity:
                flash(f"Not enough stock for {product.name}.", "error")
                return redirect(url_for("account.view_cart"))

        _stripe_set_api_key()

        line_items = []
        for pid_str, qty in cart.items():
            qty = int(qty)
            if qty <= 0:
                continue
            product = product_map.get(int(pid_str))
            if not product:
                continue

            unit_amount_pence = int((Decimal(product.price) * Decimal("100")).quantize(Decimal("1")))
            if unit_amount_pence < 0:
                continue

            line_items.append(
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {"name": product.name},
                        "unit_amount": unit_amount_pence,
                    },
                    "quantity": qty,
                }
            )

        if not line_items:
            flash("Your cart is empty.", "error")
            return redirect(url_for("account.view_cart"))

        # Save a snapshot so success handler can fulfill safely
        session["pending_checkout_cart"] = {str(k): int(v) for k, v in cart.items()}
        session["pending_checkout_shipping_address"] = shipping_address
        session.modified = True

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=url_for("account.stripe_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("account.stripe_cancel", _external=True),
            metadata={"user_id": str(user.user_id)},
        )

        record = StripeCheckoutSession(
            stripe_session_id=checkout_session.id,
            user_id=user.user_id,
            cart_json=json.dumps({str(k): int(v) for k, v in cart.items()}),
            shipping_address=shipping_address,
            payment_status="pending",
            fulfilled=False,
        )
        db.session.add(record)
        db.session.commit()

        session["pending_stripe_session_id"] = checkout_session.id
        session.modified = True

        return redirect(checkout_session.url, code=303)

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


@account_bp.route("/stripe/success")
def stripe_success():
    if not require_login():
        return redirect(url_for("auth.register_page"))

    if not _stripe_configured():
        flash("Stripe is not configured.", "error")
        return redirect(url_for("account.checkout"))

    session_id = request.args.get("session_id")
    pending_session_id = session.get("pending_stripe_session_id")
    if not session_id or not pending_session_id or session_id != pending_session_id:
        flash("Invalid checkout session.", "error")
        return redirect(url_for("account.view_cart"))

    _stripe_set_api_key()
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    if getattr(checkout_session, "payment_status", None) != "paid":
        flash("Payment not completed.", "error")
        return redirect(url_for("account.checkout"))

    record = StripeCheckoutSession.query.get(session_id)
    if record and record.payment_status != "paid":
        record.payment_status = "paid"
        db.session.commit()

    created_order_ids = _fulfill_paid_checkout(session_id, user_id=session["user_id"])

    # Clear cart + pending checkout snapshot
    session.pop("cart", None)
    session.pop("pending_stripe_session_id", None)
    session["last_order_ids"] = created_order_ids

    return redirect(url_for("account.order_confirmation"))


@account_bp.route("/stripe/cancel")
def stripe_cancel():
    flash("Checkout cancelled.", "error")
    return redirect(url_for("account.checkout"))


@account_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    if not _stripe_configured():
        return ("Stripe not configured", 400)

    secret = _stripe_webhook_secret()
    if not secret:
        return ("Webhook secret not configured", 400)

    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature")
    if not sig_header:
        return ("Missing Stripe-Signature", 400)

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=secret)
    except Exception:
        return ("Invalid signature", 400)

    # `event` is a StripeObject (not a dict), so use attribute access.
    event_type = getattr(event, "type", None)
    if event_type == "checkout.session.completed":
        data_obj = getattr(event, "data", None)
        session_obj = getattr(data_obj, "object", None)
        stripe_session_id = getattr(session_obj, "id", None)
        payment_status = getattr(session_obj, "payment_status", None)
        if stripe_session_id and payment_status == "paid":
            record = StripeCheckoutSession.query.get(stripe_session_id)
            if record and record.payment_status != "paid":
                record.payment_status = "paid"
                db.session.commit()
            _fulfill_paid_checkout(stripe_session_id)

    return ("ok", 200)



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


@account_bp.route("/order/<int:order_id>")
def order_detail(order_id):

    if not require_login():
        return redirect(url_for("auth.register_page"))

    order = Order.query.get_or_404(order_id)
    if order.buyer_id != session["user_id"]:
        abort(404)

    return render_template("account/order_detail.html", order=order)


@account_bp.route("/order/<int:order_id>/cancel", methods=["POST"])
def order_cancel(order_id):

    if not require_login():
        return redirect(url_for("auth.register_page"))

    order = Order.query.get_or_404(order_id)
    if order.buyer_id != session["user_id"]:
        abort(404)

    if order.delivery_status != "processing":
        flash("This order can no longer be cancelled.", "error")
        return redirect(url_for("account.order_detail", order_id=order_id))

    user = User.query.get(session["user_id"])

    # Restore product stock for each item
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock_quantity += item.quantity
            if product.status == "sold_out":
                product.status = "active"

    # Record refund transaction (note: Stripe refunds are not automated here)
    tx = Transaction(
        user_id=user.user_id,
        related_order_id=order.order_id,
        transaction_type="refund",
        amount=order.total_amount,
    )
    db.session.add(tx)

    order.delivery_status = "cancelled"
    order.payment_status = "cancelled"
    db.session.commit()

    flash("Order cancelled.", "success")
    return redirect(url_for("account.order_detail", order_id=order_id))

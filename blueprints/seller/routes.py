import os
import uuid
from functools import wraps

from flask import (
    render_template, request, redirect,
    url_for, session, flash, current_app
)
from werkzeug.utils import secure_filename

from . import seller_bp
from database import db
from models import User, Product, Category, Order
from forms import ProductForm


# ---------------------------------------
# HELPER: Require seller/admin role
# ---------------------------------------
def seller_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in to access that page.", "error")
            return redirect(url_for("auth.register_page"))

        user = User.query.get(user_id)
        if not user or user.role not in ("seller", "admin", "super_admin"):
            flash("You do not have permission to access that page.", "error")
            return redirect(url_for("home.home"))

        return view_func(*args, **kwargs)

    return wrapped


# ---------------------------------------
# HELPER: Save uploaded image & delete old
# ---------------------------------------
def _save_product_image(upload_file, existing_path=None):
    """
    Save an uploaded image into static/images/products,
    optionally deleting the previous image file.
    Returns the URL path (e.g. /static/images/products/xyz.png)
    or existing_path if no valid file is provided.
    """
    if not upload_file:
        return existing_path

    filename = secure_filename(upload_file.filename)
    if not filename:
        return existing_path

    # Ensure folder exists
    upload_folder = os.path.join(
        current_app.root_path, "static", "images", "products"
    )
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(upload_folder, unique_name)

    # Save new file
    upload_file.save(save_path)

    # Delete old file if it's in our products folder
    if existing_path and existing_path.startswith("/static/images/products/"):
        old_fs_path = os.path.join(
            current_app.root_path,
            existing_path.lstrip("/").replace("/", os.sep)
        )
        if os.path.exists(old_fs_path):
            try:
                os.remove(old_fs_path)
            except OSError:
                # Fail silently – not critical
                pass

    return f"/static/images/products/{unique_name}"


# ---------------------------------------
# SELLER DASHBOARD
# ---------------------------------------
@seller_bp.route("/dashboard")
@seller_required
def dashboard():
    user_id = session["user_id"]
    products = (
        Product.query
        .filter_by(seller_id=user_id)
        .order_by(Product.date_added.desc())
        .all()
    )
    total_products = len(products)
    active_products = sum(1 for p in products if p.status == "active")
    sold_products = sum(1 for p in products if p.status == "sold_out")
    recent_products = products[:5]
    return render_template(
        "seller/dashboard.html",
        products=products,
        total_products=total_products,
        active_products=active_products,
        sold_products=sold_products,
        recent_products=recent_products,
    )


# ---------------------------------------
# ADD PRODUCT
# ---------------------------------------
@seller_bp.route("/add-product", methods=["GET", "POST"])
@seller_required
def add_product():
    form = ProductForm()

    # Populate dropdown
    categories = Category.query.order_by(Category.category_name).all()
    form.category_id.choices = [(c.category_id, c.category_name) for c in categories]

    if form.validate_on_submit():
        user_id = session["user_id"]

        # -----------------------------------------------------
        # IMAGE HANDLING
        # -----------------------------------------------------
        upload = form.image.data              # <-- FIXED
        url = form.image_url.data.strip() if form.image_url.data else None

        image_path = None

        # Prefer uploaded image
        if upload:
            filename = secure_filename(upload.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"

            upload_folder = os.path.join(current_app.root_path, "static/images/products")
            os.makedirs(upload_folder, exist_ok=True)

            save_path = os.path.join(upload_folder, unique_name)
            upload.save(save_path)

            image_path = f"/static/images/products/{unique_name}"

        # Otherwise use manual URL
        elif url:
            image_path = url


        # -----------------------------------------------------
        # CREATE PRODUCT
        # -----------------------------------------------------
        product = Product(
            seller_id=user_id,
            category_id=form.category_id.data or None,
            name=form.name.data,
            description=form.description.data,
            brand=form.brand.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            condition=form.condition.data or None,
            image_url=image_path,
            status="active",
        )

        db.session.add(product)
        db.session.commit()

        flash("Product created successfully.", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template("seller/add_product.html", form=form)


# ---------------------------------------
# EDIT PRODUCT
# ---------------------------------------
@seller_bp.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
@seller_required
def edit_product(product_id):
    user_id = session["user_id"]
    product = Product.query.filter_by(
        product_id=product_id,
        seller_id=user_id
    ).first_or_404()

    form = ProductForm(obj=product)

    # Load categories
    categories = Category.query.order_by(Category.category_name).all()
    form.category_id.choices = [(c.category_id, c.category_name) for c in categories]

    if form.validate_on_submit():
        upload = form.image.data               # <-- FIXED
        image_url_text = form.image_url.data.strip() if form.image_url.data else None

        if upload:
            product.image_url = _save_product_image(
                upload_file=upload,
                existing_path=product.image_url
            )
        elif image_url_text:
            product.image_url = image_url_text

        # Update other fields
        product.name = form.name.data
        product.description = form.description.data
        product.brand = form.brand.data
        product.price = form.price.data
        product.stock_quantity = form.stock_quantity.data
        product.condition = form.condition.data or None
        product.category_id = form.category_id.data or None

        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("seller.dashboard"))

    form.category_id.data = product.category_id

    return render_template("seller/edit_product.html", form=form, product=product)


# ---------------------------------------
# DELETE PRODUCT (soft delete)
# ---------------------------------------
@seller_bp.route("/delete-product/<int:product_id>", methods=["POST"])
@seller_required
def delete_product(product_id):
    user_id = session["user_id"]
    product = Product.query.filter_by(
        product_id=product_id,
        seller_id=user_id
    ).first_or_404()

    # Soft delete
    product.status = "removed"
    db.session.commit()

    flash("Product removed.", "success")
    return redirect(url_for("seller.dashboard"))


# ---------------------------------------
# MY PRODUCTS (alias of dashboard list)
# ---------------------------------------
@seller_bp.route("/my-products")
@seller_required
def my_products():
    user_id = session["user_id"]
    products = (
        Product.query
        .filter_by(seller_id=user_id)
        .order_by(Product.date_added.desc())
        .all()
    )
    return render_template("seller/my_products.html", products=products)


# ---------------------------------------
# SELLER ORDERS (sales received)
# ---------------------------------------
@seller_bp.route("/orders")
@seller_required
def seller_orders():
    """All orders where the current user is the seller."""
    user_id = session["user_id"]

    orders = (
        Order.query
        .filter_by(seller_id=user_id)
        .order_by(Order.order_date.desc())
        .all()
    )

    return render_template("seller/orders.html", orders=orders)


@seller_bp.route("/orders/<int:order_id>/update", methods=["POST"])
@seller_required
def update_order_status(order_id):
    """Update delivery status: processing -> shipped / delivered."""
    user_id = session["user_id"]

    order = Order.query.filter_by(
        order_id=order_id,
        seller_id=user_id
    ).first_or_404()

    action = request.form.get("action")

    if action == "ship":
        order.delivery_status = "shipped"
        flash("Order marked as shipped.", "success")
    elif action == "deliver":
        order.delivery_status = "delivered"
        flash("Order marked as delivered.", "success")
    else:
        flash("Unknown action.", "error")

    db.session.commit()
    return redirect(url_for("seller.seller_orders"))

from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps

from . import seller_bp
from database import db
from models import User, Product, Category
from forms import ProductForm


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

        # Attach user if you ever want it
        return view_func(*args, **kwargs)

    return wrapped


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
    return render_template("seller/dashboard.html", products=products)


@seller_bp.route("/add-product", methods=["GET", "POST"])
@seller_required
def add_product():
    form = ProductForm()

    # populate category dropdown
    categories = Category.query.order_by(Category.category_name).all()
    form.category_id.choices = [(c.category_id, c.category_name) for c in categories]

    if form.validate_on_submit():
        user_id = session["user_id"]

        product = Product(
            seller_id=user_id,
            category_id=form.category_id.data or None,
            name=form.name.data,
            description=form.description.data,
            brand=form.brand.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            condition=form.condition.data or None,
            image_url=form.image_url.data or None,
            status="active",
        )

        db.session.add(product)
        db.session.commit()
        flash("Product created successfully.", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template("seller/add_product.html", form=form)


@seller_bp.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
@seller_required
def edit_product(product_id):
    user_id = session["user_id"]
    product = Product.query.filter_by(product_id=product_id, seller_id=user_id).first_or_404()

    form = ProductForm(obj=product)

    categories = Category.query.order_by(Category.category_name).all()
    form.category_id.choices = [(c.category_id, c.category_name) for c in categories]

    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.brand = form.brand.data
        product.price = form.price.data
        product.stock_quantity = form.stock_quantity.data
        product.condition = form.condition.data or None
        product.image_url = form.image_url.data or None
        product.category_id = form.category_id.data or None

        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("seller.dashboard"))

    # preset category in form
    form.category_id.data = product.category_id
    return render_template("seller/edit_product.html", form=form, product=product)


@seller_bp.route("/delete-product/<int:product_id>", methods=["POST"])
@seller_required
def delete_product(product_id):
    user_id = session["user_id"]
    product = Product.query.filter_by(product_id=product_id, seller_id=user_id).first_or_404()

    # soft delete: mark as removed
    product.status = "removed"
    db.session.commit()
    flash("Product removed.", "success")
    return redirect(url_for("seller.dashboard"))

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

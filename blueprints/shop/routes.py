from datetime import datetime

from flask import (
    render_template, redirect, url_for,
    flash, session, request
)

from database import db
from . import shop_bp
from models import Product, Review, Order, OrderItem, Category
from forms import ReviewForm
from sqlalchemy import func


# -------------------------------------------------
# MAIN SHOP PAGE / SEARCH ENTRY
# -------------------------------------------------
@shop_bp.route("/")
def shop():
    """
    If there's a ?q= search query, send to /search.
    If not, just go back to the home page.
    This avoids needing a shop/shop.html template.
    """
    query = request.args.get("q", "").strip()

    if query:
        return redirect(url_for("shop.search", q=query))

    # No search term → just go home (or you could later make a real shop landing page)
    return redirect(url_for("home.home"))


# -------------------------------------------------
# PRODUCT PAGE + REVIEWS
# -------------------------------------------------
@shop_bp.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    user_id = session.get("user_id")
    user_has_bought = False
    existing_review = None

    # Check if user purchased this product
    if user_id:
        user_has_bought = (
            db.session.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.order_id)
            .filter(
                OrderItem.product_id == product_id,
                Order.buyer_id == user_id
            )
            .first()
            is not None
        )

        # If review exists, load it for editing
        existing_review = Review.query.filter_by(
            product_id=product_id,
            user_id=user_id
        ).first()

        if request.method == "GET" and existing_review:
            form.rating.data = existing_review.rating
            form.review_text.data = existing_review.review_text

        # Handle review submit
        if request.method == "POST" and form.validate_on_submit():

            if not user_has_bought:
                flash("Only verified buyers can leave a review.", "error")
                return redirect(url_for("shop.product_page", product_id=product_id))

            if existing_review:
                # Update review
                existing_review.rating = form.rating.data
                existing_review.review_text = form.review_text.data
                existing_review.edited_at = datetime.utcnow()
                flash("Your review has been updated.", "success")

            else:
                new_review = Review(
                    product_id=product_id,
                    user_id=user_id,
                    rating=form.rating.data,
                    review_text=form.review_text.data,
                )
                db.session.add(new_review)
                flash("Your review has been submitted.", "success")

            db.session.commit()
            return redirect(url_for("shop.product_page", product_id=product_id))

    # Review stats
    average_rating = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.product_id == product_id)
        .scalar()
    ) or 0

    review_count = Review.query.filter_by(product_id=product_id).count()

    reviews = (
        Review.query
        .filter_by(product_id=product_id)
        .order_by(Review.date_posted.desc())
        .all()
    )

    return render_template(
        "shop/product_page.html",
        product=product,
        form=form,
        reviews=reviews,
        user_has_bought=user_has_bought,
        existing_review=existing_review,
        average_rating=average_rating,
        review_count=review_count,
    )


# -------------------------------------------------
# DELETE REVIEW
# -------------------------------------------------
@shop_bp.route("/product/<int:product_id>/review/delete", methods=["POST"])
def delete_review(product_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in.", "error")
        return redirect(url_for("auth.register_page"))

    review = Review.query.filter_by(
        product_id=product_id,
        user_id=user_id
    ).first_or_404()

    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "success")

    return redirect(url_for("shop.product_page", product_id=product_id))


# ============================================================
# CATEGORY SYSTEM — DB-DRIVEN (SAFE)
# ============================================================

# Maps URL slugs → actual category names in the DB
SLUG_TO_CATEGORY_NAME = {
    "cpu": "CPU",
    "gpu": "GPU",
    "motherboard": "Motherboard",
    "ram": "RAM",
    "storage": "Storage",
    "power-supplies": "Power Supplies",
    "games": "Games",
    "accessories": "Accessories",
    "prebuilt": "Prebuilt",
    "repair-upgrade": "Repair & Upgrade",
    "consultation": "Consultation",
}


@shop_bp.route("/category/<slug>")
def category_page(slug):
    """Dynamic category listing, 100% accurate to DB contents."""
    page = request.args.get("page", 1, type=int)

    category_name = SLUG_TO_CATEGORY_NAME.get(slug)
    if not category_name:
        return render_template("shop/category_not_found.html", slug=slug), 404

    # Get actual category row from DB
    category = Category.query.filter_by(category_name=category_name).first_or_404()

    # Query all active products in this category
    products = (
        Product.query
        .filter_by(category_id=category.category_id, status="active")
        .order_by(Product.date_added.desc())
        .paginate(page=page, per_page=12)
    )

    return render_template(
        "shop/category_page.html",
        products=products,
        slug=slug,
        category=category,
    )


# -------------------------------------------------
# SEARCH
# -------------------------------------------------
@shop_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        # No query — could redirect to home or show empty list
        return render_template("shop/search_results.html", products=[], query=query)

    products = Product.query.filter(
        Product.status == "active",
        Product.name.ilike(f"%{query}%")
    ).order_by(Product.date_added.desc()).all()

    return render_template(
        "shop/search_results.html",
        products=products,
        query=query
    )

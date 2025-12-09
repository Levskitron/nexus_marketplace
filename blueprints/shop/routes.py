from datetime import datetime

from flask import (
    render_template, redirect, url_for,
    flash, session, request
)

from database import db
from . import shop_bp
from models import Product, Review, Order, OrderItem
from forms import ReviewForm
from sqlalchemy import func


# ----------------------------
# MAIN SHOP PAGE
# ----------------------------
@shop_bp.route("/")
def shop():
    return render_template("shop/shop.html")


# ----------------------------
# PRODUCT PAGE + REVIEWS
# ----------------------------
@shop_bp.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    user_id = session.get("user_id")
    user_has_bought = False
    existing_review = None

    # ----------------------------
    # CHECK IF USER PURCHASED PRODUCT
    # ----------------------------
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

        # Review exists?
        existing_review = Review.query.filter_by(
            product_id=product_id,
            user_id=user_id
        ).first()

        # Pre-fill form when editing
        if request.method == "GET" and existing_review:
            form.rating.data = existing_review.rating
            form.review_text.data = existing_review.review_text

        # Handle review submit
        if request.method == "POST" and form.validate_on_submit():
            if not user_has_bought:
                flash("Only verified buyers can leave a review.", "error")
                return redirect(url_for("shop.product_page", product_id=product_id))

            if existing_review:
                # Update existing review
                existing_review.rating = form.rating.data
                existing_review.review_text = form.review_text.data
                existing_review.edited_at = datetime.utcnow()
                flash("Your review has been updated.", "success")
            else:
                # Create new review
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

    # ----------------------------
    # REVIEW STATS
    # ----------------------------
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


# ----------------------------
# DELETE REVIEW
# ----------------------------
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
# CATEGORY SYSTEM (REPLACES CPU/GPU/RAM/... ROUTES)
# ============================================================

CATEGORY_MAP = {
    "cpu": 1,
    "gpu": 2,
    "motherboard": 3,
    "ram": 4,
    "storage": 5,
    "power-supplies": 6,
    "games": 7,
    "accessories": 8,
    "prebuilt": 9,
    "repair-upgrade": 10,
    "consultation": 11,
}

@shop_bp.route("/category/<slug>")
def category_page(slug):
    """Dynamic category listing with pagination."""
    page = request.args.get("page", 1, type=int)

    if slug not in CATEGORY_MAP:
        return render_template("shop/category_not_found.html"), 404

    category_id = CATEGORY_MAP[slug]

    products = Product.query.filter_by(
        category_id=category_id,
        status="active"
    ).order_by(Product.date_added.desc()).paginate(page=page, per_page=12)

    return render_template(
        "shop/category_page.html",
        products=products,
        slug=slug
    )

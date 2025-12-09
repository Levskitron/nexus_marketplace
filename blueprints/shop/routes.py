from datetime import datetime

from flask import (
    render_template, redirect, url_for,
    flash, session, request
)

from database import db
from . import shop_bp
from models import Product, Review, Order, OrderItem
from forms import ReviewForm


# ----------------------------
# MAIN SHOP PAGE (optional)
# ----------------------------
@shop_bp.route("/")
def shop():
    return render_template("shop/shop.html")


# ----------------------------
# DYNAMIC PRODUCT PAGE
# ----------------------------
@shop_bp.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    user_id = session.get("user_id")
    user_has_bought = False
    existing_review = None

    # --- Check if user has bought this product ---
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

        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            product_id=product_id,
            user_id=user_id
        ).first()

        # Pre-fill form with existing review on GET
        if request.method == "GET" and existing_review:
            form.rating.data = existing_review.rating
            form.review_text.data = existing_review.review_text

        # Handle review submit / update
        if request.method == "POST" and form.validate_on_submit():
            if not user_has_bought:
                flash("Only buyers of this product can leave a review.", "error")
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

    # --- Aggregate review stats ---
    average_rating = (
        db.session.query(db.func.avg(Review.rating))
        .filter(Review.product_id == product_id)
        .scalar()
    )
    review_count = Review.query.filter_by(product_id=product_id).count()

    return render_template(
        "shop/product_page.html",
        product=product,
        form=form,
        user_has_bought=user_has_bought,
        existing_review=existing_review,
        average_rating=average_rating,
        review_count=review_count,
    )


# ----------------------------
# DELETE REVIEW (for current user)
# ----------------------------
@shop_bp.route("/product/<int:product_id>/review/delete", methods=["POST"])
def delete_review(product_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to delete a review.", "error")
        return redirect(url_for("auth.register_page"))

    review = Review.query.filter_by(
        product_id=product_id,
        user_id=user_id
    ).first_or_404()

    db.session.delete(review)
    db.session.commit()
    flash("Your review has been deleted.", "success")

    return redirect(url_for("shop.product_page", product_id=product_id))


# ----------------------------
# PC PARTS
# ----------------------------
@shop_bp.route("/pc-parts/cpu")
def cpu():
    return render_template("shop/pc_parts/cpu.html")


@shop_bp.route("/pc-parts/gpu")
def gpu():
    return render_template("shop/pc_parts/gpu.html")


@shop_bp.route("/pc-parts/motherboard")
def motherboard():
    return render_template("shop/pc_parts/motherboard.html")


@shop_bp.route("/pc-parts/ram")
def ram():
    return render_template("shop/pc_parts/ram.html")


@shop_bp.route("/pc-parts/storage")
def storage():
    return render_template("shop/pc_parts/storage.html")


@shop_bp.route("/pc-parts/power-supplies")
def power_supplies():
    return render_template("shop/pc_parts/power_supplies.html")


# ----------------------------
# GAMES & ACCESSORIES
# ----------------------------
@shop_bp.route("/games-accessories/games")
def games():
    return render_template("shop/games_accessories/games.html")


@shop_bp.route("/games-accessories/accessories")
def accessories():
    return render_template("shop/games_accessories/accessories.html")


# ----------------------------
# SERVICES
# ----------------------------
@shop_bp.route("/services/prebuilt")
def prebuilt():
    return render_template("shop/services/prebuilt.html")


@shop_bp.route("/services/repair-upgrade")
def repair_upgrade():
    return render_template("shop/services/repair_upgrade.html")


@shop_bp.route("/services/consultation")
def consultation():
    return render_template("shop/services/consultation.html")

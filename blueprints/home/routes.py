from flask import render_template, session
from . import home_bp

from database import db
from models import Product, OrderItem
from sqlalchemy import func
import random


# -------------------------------------------
# HOME PAGE (Recommended + Trending Products)
# -------------------------------------------
@home_bp.route("/")
def home():

    # ----------------------------
    #  RECOMMENDED PRODUCTS (Random 3)
    # ----------------------------
    recommended = Product.query.filter_by(status="active").all()
    random.shuffle(recommended)
    recommended = recommended[:3]

    # ----------------------------
    #  TRENDING PRODUCTS (Top 3 by sales)
    # ----------------------------
    trending = (
        db.session.query(Product)
        .join(OrderItem, Product.product_id == OrderItem.product_id)
        .group_by(Product.product_id)
        .order_by(func.count(OrderItem.order_id).desc())
        .limit(3)
        .all()
    )

    return render_template(
        "home/home.html",
        username=session.get("username"),
        email=session.get("email"),
        recommended=recommended,
        trending=trending
    )


# -------------------------------------------
# STATIC PAGES
# -------------------------------------------
@home_bp.route("/about")
def about():
    return render_template("home/about.html")


@home_bp.route("/policies")
def policies():
    return render_template("home/policies.html")


@home_bp.route("/our-story")
def our_story():
    return render_template("home/our_story.html")


@home_bp.route("/support")
def support():
    return render_template("account/support.html")

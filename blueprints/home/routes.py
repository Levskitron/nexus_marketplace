from flask import render_template, session, request, flash, redirect, url_for, current_app
from . import home_bp

from database import db
from models import Product, OrderItem
from sqlalchemy import func
import random
import smtplib
from email.message import EmailMessage


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


@home_bp.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        message = (request.form.get("message") or "").strip()

        if not name or not email or not message:
            flash("Please fill in all fields before sending your message.", "error")
            return redirect(url_for("home.support"))

        try:
            app = current_app
            support_email = app.config.get("SUPPORT_EMAIL")

            msg = EmailMessage()
            msg["Subject"] = f"Nexus support request from {name}"
            msg["From"] = app.config.get("MAIL_USERNAME") or support_email
            msg["To"] = support_email
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            msg.set_content(body)

            with smtplib.SMTP(app.config.get("MAIL_SERVER"), app.config.get("MAIL_PORT")) as server:
                if app.config.get("MAIL_USE_TLS"):
                    server.starttls()
                if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
                    server.login(app.config.get("MAIL_USERNAME"), app.config.get("MAIL_PASSWORD"))
                server.send_message(msg)

            flash("Your message has been sent. We'll get back to you soon.", "success")
        except Exception:
            flash("Something went wrong while sending your message. Please try again later.", "error")

        return redirect(url_for("home.support"))

    return render_template("account/support.html")

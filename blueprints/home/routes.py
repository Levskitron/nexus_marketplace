from flask import render_template, session
from . import home_bp

@home_bp.route("/")
def home():
    return render_template(
        "home/home.html",
        username=session.get("username"),
        email=session.get("email")
    )

@home_bp.route("/about")
def about():
    return render_template("home/about.html")

@home_bp.route("/policies")
def policies():
    return render_template("home/policies.html")

@home_bp.route("/our-story")
def our_story():
    return render_template("home/our_story.html")

@home_bp.route("/contact")
def contact():
    return render_template("home/contact.html")

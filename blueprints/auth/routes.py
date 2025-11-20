from flask import render_template, request, jsonify, session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import auth_bp
from database import db
from models import User


# Page that shows the combined Sign In / Register UI
@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("auth/register.html")


# API endpoint for registering a new user
@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm_password") or ""

    # Basic validation
    if not username or not email or not password:
        return jsonify(success=False, message="All fields are required."), 400

    if password != confirm:
        return jsonify(success=False, message="Passwords do not match."), 400

    # Check if username or email already taken
    existing = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing:
        return jsonify(success=False, message="Username or email already in use."), 400

    # Create user
    hashed = generate_password_hash(password)
    user = User(
        username=username,
        email=email,
        password_hash=hashed,
        role="buyer",
        account_status="active",
        date_joined=datetime.utcnow(),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(success=True, message="Account created successfully. You can now sign in."), 200


# API endpoint for logging in
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify(success=False, message="Both fields are required."), 400

    user = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify(success=False, message="Invalid username or password."), 401

    # Save session (for later use on other pages)
    session["user_id"] = user.user_id
    session["username"] = user.username

    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify(success=True, message="Logged in successfully."), 200

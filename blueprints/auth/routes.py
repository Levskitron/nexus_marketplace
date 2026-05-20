from flask import render_template, request, jsonify, session
from flask import redirect, url_for
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import auth_bp
from database import db
from models import User


# PAGE: Combined Sign In / Register UI
@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("auth/register.html")


# API: Register a new user (called via fetch from JS)
@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm_password") or ""

    # Basic validation
    if not username or not email or not password or not confirm:
        return jsonify(success=False, message="All fields are required."), 400

    if password != confirm:
        return jsonify(success=False, message="Passwords do not match."), 400

    # Check if username OR email already in use
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify(success=False, message="Username or email already in use."), 400

    # Hash password
    password_hash = generate_password_hash(password)

    # Create user
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role="buyer",
        account_status="active",
        date_joined=datetime.utcnow(),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(success=True, message="Account created successfully. You can now sign in."), 200


# API: Login (called via fetch from JS)
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

    # Save user details into session
    session["user_id"] = user.user_id
    session["username"] = user.username
    session["email"] = user.email  

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify(success=True, message="Logged in successfully."), 200

# API: Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.register_page"))



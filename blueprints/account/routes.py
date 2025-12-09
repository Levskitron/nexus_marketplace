from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import account_bp
from database import db
from models import User


# --- PROTECT PAGE (must be logged in) ---
def require_login():
    if not session.get("user_id"):
        return False
    return True


# --- PAGE: My Account ---
@account_bp.route("/my-account", methods=["GET", "POST"])
def my_account():

    # User must be logged in
    if not require_login():
        return redirect(url_for("auth.register_page"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        action = request.form.get("action")

        # --- UPDATE USERNAME ---
        if action == "update_username":
            new_username = request.form.get("new_username").strip()
            if new_username:
                user.username = new_username
                session["username"] = new_username
                db.session.commit()
                flash("Username updated!", "success")

        # --- UPDATE PASSWORD ---
        elif action == "update_password":
            new_password = request.form.get("new_password")
            if new_password:
                user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash("Password updated!", "success")

        # --- UPDATE EMAIL ---
        elif action == "update_email":
            new_email = request.form.get("new_email").strip().lower()
            if new_email:
                user.email = new_email
                session["email"] = new_email
                db.session.commit()
                flash("Email updated!", "success")

        # (Optional) Checkbox settings
        elif action == "update_settings":
            flash("Settings saved.", "success")

        return redirect(url_for("account.my_account"))

    return render_template("account/my_account.html", user=user)

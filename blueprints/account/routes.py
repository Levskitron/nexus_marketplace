from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from . import account_bp
from database import db
from models import User, Product


# --- PROTECT PAGE (must be logged in) ---
def require_login():
    return bool(session.get("user_id"))


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
            new_username = request.form.get("new_username", "").strip()
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
            new_email = request.form.get("new_email", "").strip().lower()
            if new_email:
                user.email = new_email
                session["email"] = new_email
                db.session.commit()
                flash("Email updated!", "success")

        # --- UPDATE SETTINGS ---
        elif action == "update_settings":
            flash("Settings saved.", "success")

        # --- BECOME A SELLER ---
        elif action == "become_seller":
            if user.role == "buyer":
                user.role = "seller"
                db.session.commit()
                flash("Your account is now a seller account! You can now list products.", "success")
                return redirect(url_for("seller.dashboard"))
            else:
                flash("You are already a seller or higher.", "info")

        # --- REMOVE SELLER ROLE (Option A: only if no products) ---
        elif action == "remove_seller_role":
            if user.role == "seller":
                # Check if user has active products
                active_products = Product.query.filter_by(
                    seller_id=user.user_id,
                    status="active"
                ).count()

                if active_products > 0:
                    flash("You cannot remove seller status while you still have active product listings.", "error")
                else:
                    user.role = "buyer"
                    db.session.commit()
                    flash("Seller role removed. You are now a regular buyer.", "success")
            else:
                flash("You are not a seller.", "info")

        return redirect(url_for("account.my_account"))

    return render_template("account/my_account.html", user=user)

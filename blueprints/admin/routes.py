from functools import wraps

from flask import (
    render_template, request, redirect,
    url_for, session, flash, abort
)
from werkzeug.security import generate_password_hash

from . import admin_bp
from database import db
from models import User, Product, Order, AdminLog


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in to access the admin area.", "error")
            return redirect(url_for("auth.register_page"))
        user = User.query.get(user_id)
        if not user or user.role not in ("admin", "super_admin"):
            flash("You do not have permission to access that page.", "error")
            return redirect(url_for("home.home"))
        return view_func(*args, **kwargs)
    return wrapped


def super_admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in.", "error")
            return redirect(url_for("auth.register_page"))
        user = User.query.get(user_id)
        if not user or user.role != "super_admin":
            flash("Only super admins can perform this action.", "error")
            return redirect(url_for("admin.dashboard"))
        return view_func(*args, **kwargs)
    return wrapped


def _log_admin_action(admin_id, action, affected_user_id=None):
    log = AdminLog(
        admin_id=admin_id,
        affected_user_id=affected_user_id,
        action=action,
    )
    db.session.add(log)


def _can_delete_user(current, target):
    """Admins cannot delete super_admins. No one can delete self if last super_admin."""
    if target.user_id == current.user_id:
        if current.role != "super_admin":
            return False
        other = User.query.filter(User.role == "super_admin", User.user_id != current.user_id).count()
        return other > 0
    if current.role == "admin" and target.role == "super_admin":
        return False
    return True


# ---------------------------------------
# DASHBOARD
# ---------------------------------------
@admin_bp.route("/")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    recent_logs = (
        AdminLog.query
        .order_by(AdminLog.timestamp.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        recent_logs=recent_logs,
    )


# ---------------------------------------
# USER MANAGEMENT
# ---------------------------------------
@admin_bp.route("/users")
@admin_required
def users():
    current = User.query.get(session["user_id"])
    users_list = User.query.order_by(User.date_joined.desc()).all()
    can_delete_ids = {u.user_id for u in users_list if _can_delete_user(current, u)}
    return render_template(
        "admin/users.html",
        users_list=users_list,
        can_delete_ids=can_delete_ids,
    )


@admin_bp.route("/users/<int:user_id>/update", methods=["POST"])
@admin_required
def update_user(user_id):
    current = User.query.get(session["user_id"])
    target = User.query.get_or_404(user_id)

    new_role = request.form.get("role", "").strip()
    new_status = request.form.get("account_status", "").strip()

    # Only super_admin can set role to admin or super_admin
    if new_role in ("admin", "super_admin") and current.role != "super_admin":
        flash("Only a super admin can promote users to admin or super admin.", "error")
        return redirect(url_for("admin.users"))

    # Cannot demote yourself from super_admin if you're the last one
    if target.user_id == current.user_id and new_role != "super_admin" and current.role == "super_admin":
        other_super = User.query.filter(User.role == "super_admin", User.user_id != current.user_id).count()
        if other_super == 0:
            flash("You cannot remove your own super admin role while you are the only super admin.", "error")
            return redirect(url_for("admin.users"))

    changed = False
    if new_role and new_role in ("buyer", "seller", "admin", "super_admin") and new_role != target.role:
        target.role = new_role
        _log_admin_action(current.user_id, f"Changed role of user {target.username} (id={target.user_id}) to {new_role}", target.user_id)
        changed = True

    if new_status and new_status in ("active", "suspended", "deleted") and new_status != target.account_status:
        target.account_status = new_status
        _log_admin_action(current.user_id, f"Changed account_status of user {target.username} (id={target.user_id}) to {new_status}", target.user_id)
        changed = True

    if changed:
        db.session.commit()
        flash("User updated.", "success")
    else:
        flash("No changes made.", "error")

    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    current = User.query.get(session["user_id"])
    target = User.query.get_or_404(user_id)
    # Admins cannot edit super_admin users
    if current.role == "admin" and target.role == "super_admin":
        flash("You cannot edit a super admin.", "error")
        return redirect(url_for("admin.users"))

    if request.method == "POST":
        new_username = (request.form.get("username") or "").strip()
        new_email = (request.form.get("email") or "").strip().lower()
        if not new_username:
            flash("Username is required.", "error")
            return redirect(url_for("admin.edit_user", user_id=user_id))
        if not new_email:
            flash("Email is required.", "error")
            return redirect(url_for("admin.edit_user", user_id=user_id))
        # Unique check (excluding self)
        if User.query.filter(User.username == new_username, User.user_id != target.user_id).first():
            flash("That username is already in use.", "error")
            return redirect(url_for("admin.edit_user", user_id=user_id))
        if User.query.filter(User.email == new_email, User.user_id != target.user_id).first():
            flash("That email is already in use.", "error")
            return redirect(url_for("admin.edit_user", user_id=user_id))
        target.username = new_username
        target.email = new_email
        _log_admin_action(current.user_id, f"Edited user id={target.user_id} to username={new_username}, email={new_email}", target.user_id)
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_edit.html", target=target)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    current = User.query.get(session["user_id"])
    target = User.query.get_or_404(user_id)

    if not _can_delete_user(current, target):
        flash("You cannot delete this user.", "error")
        return redirect(url_for("admin.users"))

    target.account_status = "deleted"
    _log_admin_action(current.user_id, f"Deleted user {target.username} (id={target.user_id})", target.user_id)
    db.session.commit()
    flash("User has been deleted.", "success")
    return redirect(url_for("admin.users"))


# ---------------------------------------
# ADD ADMIN USER (super_admin only)
# ---------------------------------------
@admin_bp.route("/users/add", methods=["GET", "POST"])
@super_admin_required
def add_admin_user():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        role = (request.form.get("role") or "").strip()

        if not username or not email or not password:
            flash("Username, email and password are required.", "error")
            return redirect(url_for("admin.add_admin_user"))
        if role not in ("admin", "super_admin"):
            flash("Role must be admin or super_admin.", "error")
            return redirect(url_for("admin.add_admin_user"))
        if User.query.filter_by(username=username).first():
            flash("That username is already in use.", "error")
            return redirect(url_for("admin.add_admin_user"))
        if User.query.filter_by(email=email).first():
            flash("That email is already in use.", "error")
            return redirect(url_for("admin.add_admin_user"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            account_status="active",
        )
        db.session.add(user)
        _log_admin_action(
            session["user_id"],
            f"Created {role} user {username} (id={user.user_id})",
            user.user_id,
        )
        db.session.commit()
        flash(f"Created {role} user '{username}'.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/add_admin_user.html")


# ---------------------------------------
# PRODUCT MANAGEMENT
# ---------------------------------------
@admin_bp.route("/products")
@admin_required
def products():
    products_list = Product.query.order_by(Product.date_added.desc()).all()
    return render_template("admin/products.html", products_list=products_list)


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    current = User.query.get(session["user_id"])
    product = Product.query.get_or_404(product_id)
    product.status = "removed"
    _log_admin_action(current.user_id, f"Removed product '{product.name}' (id={product.product_id})", None)
    db.session.commit()
    flash("Product removed.", "success")
    return redirect(url_for("admin.products"))

from flask import render_template
from . import account_bp

@account_bp.route("/")
def my_account():
    return render_template("account/my_account.html")

@account_bp.route("/orders")
def order_history():
    return render_template("account/order_history.html")

@account_bp.route("/cart")
def cart():
    return render_template("account/cart.html")

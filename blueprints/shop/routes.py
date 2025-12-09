from flask import render_template
from models import Product
from . import shop_bp


# ----------------------------
# MAIN SHOP PAGE (optional)
# ----------------------------
@shop_bp.route("/")
def shop():
    return render_template("shop/shop.html")


# ----------------------------
# DYNAMIC PRODUCT PAGE
# ----------------------------
@shop_bp.route("/product/<int:product_id>")
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("shop/product_page.html", product=product)


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

from flask import render_template
from models import Product
from . import shop_bp

@shop_bp.route("/product/<int:product_id>")
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("shop/product_page.html", product=product)

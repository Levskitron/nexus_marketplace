from flask import Blueprint

seller_bp = Blueprint(
    "seller",
    __name__,
    url_prefix="/seller"
)

from . import routes

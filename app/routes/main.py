
from flask import Blueprint, render_template

from app.models import Product

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Hiển thị trang chủ MENSTYLE."""

    featured_products = (
        Product.query
        .filter_by(is_active=True)
        .order_by(Product.id.desc())
        .all()
    )

    return render_template(
        "home.html",
        products=featured_products,
    )

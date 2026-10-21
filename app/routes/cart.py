
from decimal import Decimal
from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    session,
    url_for,
    flash,
    request,
)

from app.models import Product
from app.extensions import db

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


def get_cart_items():
    """Đọc giỏ hàng và lấy thông tin sản phẩm mới nhất từ database."""

    cart = session.get("cart", {})
    items = []
    total = Decimal("0.00")

    for product_id, quantity in cart.items():
        product = db.session.get(Product, int(product_id))

        if product is None or not product.is_active or quantity <= 0:
            continue
        price = product.sale_price or product.price
        subtotal = price * quantity
        total += subtotal

        items.append({
            "product": product,
            "quantity": quantity,
            "price": price,
            "subtotal": subtotal,
        })

    return items, total


@cart_bp.route("/")
def view_cart():
    """Hiển thị giỏ hàng."""

    items, total = get_cart_items()

    return render_template(
        "cart/cart.html",
        items=items,
        total=total,
    )


@cart_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    """Thêm một sản phẩm vào giỏ hàng."""

    product = db.session.get(Product, product_id)

    if product is None:
        abort(404)

    if not product.is_active:
        flash(
            "Sản phẩm đã ngừng kinh doanh, không thể thêm vào giỏ hàng.",
            "error",
        )
        return redirect(url_for("cart.view_cart"))

    cart = session.get("cart", {})
    key = str(product.id)
    quantity = int(cart.get(key, 0))

    if product.stock <= quantity:
        flash("Sản phẩm đã đạt giới hạn tồn kho.", "error")
    else:
        cart[key] = quantity + 1
        session["cart"] = cart
        session.modified = True
        flash("Đã thêm sản phẩm vào giỏ hàng.", "success")

    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    """Cập nhật số lượng sản phẩm trong giỏ."""

    product = db.session.get(Product, product_id)

    cart = session.get("cart", {})
    key = str(product_id)

    if product is None:
        cart.pop(key, None)
        session["cart"] = cart
        session.modified = True
        flash("Sản phẩm không còn tồn tại.", "error")
        return redirect(url_for("cart.view_cart"))

    if not product.is_active:
        cart.pop(key, None)
        session["cart"] = cart
        session.modified = True
        flash(
            "Sản phẩm đã ngừng kinh doanh và được loại khỏi giỏ hàng.",
            "error",
        )
        return redirect(url_for("cart.view_cart"))
    try:
        quantity = int(request.form.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart.pop(key, None)
        flash("Đã xóa sản phẩm khỏi giỏ hàng.", "success")
    elif quantity > product.stock:
        flash("Số lượng vượt quá tồn kho.", "error")
    else:
        cart[key] = quantity
        flash("Đã cập nhật giỏ hàng.", "success")

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    """Xóa một sản phẩm khỏi giỏ."""

    cart = session.get("cart", {})
    cart.pop(str(product_id), None)

    session["cart"] = cart
    session.modified = True

    flash("Đã xóa sản phẩm khỏi giỏ hàng.", "success")

    return redirect(url_for("cart.view_cart"))

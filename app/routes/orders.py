
import secrets
from decimal import Decimal

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from sqlalchemy import select

from app.extensions import db
from app.models import Product, Order, OrderItem, Payment
from flask_login import current_user

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


def get_checkout_items():
    """Lấy sản phẩm và giá hiện tại từ database."""
    cart = session.get("cart", {})
    items = []
    subtotal = Decimal("0.00")

    for product_id, quantity in cart.items():
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        if quantity <= 0:
            continue
        
        if quantity > 100:
            continue

        product = db.session.get(Product, product_id)

        if product is None or not product.is_active:
            continue
        price = Decimal(str(
            product.sale_price
            if product.sale_price is not None
            and product.sale_price < product.price
            else product.price
        ))

        line_total = price * quantity
        items.append({
            "product": product,
            "quantity": quantity,
            "price": price,
            "subtotal": line_total,
        })
        subtotal += line_total

    return items, subtotal


@orders_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, subtotal = get_checkout_items()

    if not items:
        flash("Giỏ hàng của bạn đang trống.", "warning")
        return redirect(url_for("cart.view_cart"))

    if request.method == "POST":
        name = request.form.get("recipient_name", "").strip()
        phone = request.form.get("recipient_phone", "").strip()
        email = request.form.get("recipient_email", "").strip()
        address = request.form.get("shipping_address", "").strip()
        note = request.form.get("note", "").strip()

        errors = []

        if not 2 <= len(name) <= 150:
            errors.append("Họ tên phải từ 2 đến 150 ký tự.")
        if not 9 <= len(phone) <= 20:
            errors.append("Số điện thoại không hợp lệ.")
        if len(email) > 150:
            errors.append("Email không được vượt quá 150 ký tự.")
        if not address or len(address) > 2000:
            errors.append("Vui lòng nhập địa chỉ nhận hàng hợp lệ.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "orders/checkout.html",
                items=items,
                subtotal=subtotal,
                shipping_fee=Decimal("0.00"),
                total=subtotal,
            )

        try:
            # Khóa các hàng sản phẩm trong lúc xác nhận tồn kho.
            product_ids = [item["product"].id for item in items]
            locked_products = db.session.scalars(
                select(Product)
                .where(Product.id.in_(product_ids))
                .with_for_update()
            ).all()
            products_by_id = {
                product.id: product for product in locked_products
            }

            # Kiểm tra tồn kho và tính lại giá từ dữ liệu mới nhất.
            verified_items = []
            verified_subtotal = Decimal("0.00")
          
            for item in items:
                product = products_by_id.get(item["product"].id)

                if product is None:
                    raise ValueError("Một sản phẩm không còn tồn tại.")

                if not product.is_active:
                    raise ValueError(
                        f"Sản phẩm '{product.name}' đã ngừng kinh doanh. "
                        "Vui lòng quay lại giỏ hàng để kiểm tra."
                    )

                quantity = item["quantity"]

                if product.stock < quantity:
                    raise ValueError(
                        f"Sản phẩm '{product.name}' chỉ còn "
                        f"{product.stock} sản phẩm trong kho."
                    )

                price = Decimal(str(
                    product.sale_price
                    if product.sale_price is not None
                    and product.sale_price < product.price
                    else product.price
                ))

                line_total = price * quantity
                verified_items.append({
                    "product": product,
                    "quantity": quantity,
                    "price": price,
                    "subtotal": line_total,
                })
                verified_subtotal += line_total

            order_code = "MS" + secrets.token_hex(6).upper()

            order = Order(
                user_id=(
                    current_user.id
                    if current_user.is_authenticated
                    and current_user.role == "customer"
                    else None
                ),
                order_code=order_code,
                recipient_name=name,
                recipient_phone=phone,
                recipient_email=email or None,
                shipping_address=address,
                note=note or None,
                subtotal=verified_subtotal,
                shipping_fee=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
                total_amount=verified_subtotal,
                payment_method="COD",
                payment_status="pending",
                order_status="Chờ xác nhận",
            )
            db.session.add(order)
            db.session.flush()

            for item in verified_items:
                product = item["product"]
                quantity = item["quantity"]

                db.session.add(OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=item["price"],
                    quantity=quantity,
                    subtotal=item["subtotal"],
                ))

                # Trừ tồn kho sau khi đã xác nhận đơn hàng.
                product.stock -= quantity

            db.session.add(Payment(
                order_id=order.id,
                payment_method="COD",
                amount=verified_subtotal,
                payment_status="pending",
            ))

            db.session.commit()
            session["cart"] = {}
            session.modified = True

            return redirect(
                url_for("orders.order_success", order_code=order_code)
            )

        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            orders_bp.logger.exception("Không thể tạo đơn hàng.")
            flash(
                "Chưa thể tạo đơn hàng do lỗi hệ thống. "
                "Vui lòng thử lại.",
                "danger",
            )

        items, subtotal = get_checkout_items()

    return render_template(
        "orders/checkout.html",
        items=items,
        subtotal=subtotal,
        shipping_fee=Decimal("0.00"),
        total=subtotal,
    )


@orders_bp.route("/success/<string:order_code>")
def order_success(order_code):
    order = Order.query.filter_by(order_code=order_code).first_or_404()
    return render_template("orders/success.html", order=order)

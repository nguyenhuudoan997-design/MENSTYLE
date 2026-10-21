
"""Các route quản lý tài khoản cá nhân."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.models import User, Order, Product

from app.extensions import db
from app.models import User


account_bp = Blueprint(
    "account",
    __name__,
    url_prefix="/account",
)


@account_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    """Xem và cập nhật thông tin cá nhân."""
    if current_user.role != "customer":
        flash("Chức năng này chỉ dành cho khách hàng.", "warning")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not full_name or len(full_name) > 150:
            flash("Họ tên phải từ 1 đến 150 ký tự.", "danger")
            return render_template("account/profile.html")

        if phone and len(phone) > 20:
            flash("Số điện thoại không được vượt quá 20 ký tự.", "danger")
            return render_template("account/profile.html")

        current_user.full_name = full_name
        current_user.phone = phone or None

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Không thể cập nhật thông tin. Vui lòng thử lại.", "danger")
            return render_template("account/profile.html")

        flash("Cập nhật thông tin cá nhân thành công.", "success")
        return redirect(url_for("account.profile"))

    return render_template("account/profile.html")
from app.models import Order


@account_bp.route("/orders")
@login_required
def order_history():
    if current_user.role != "customer":
        flash("Chức năng này chỉ dành cho khách hàng.", "warning")
        return redirect(url_for("main.home"))

    orders = (
        Order.query
        .filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template(
        "account/orders.html",
        orders=orders
    )
@account_bp.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    if current_user.role != "customer":
        flash("Chức năng này chỉ dành cho khách hàng.", "warning")
        return redirect(url_for("main.home"))

    # Chỉ cho phép xem đơn hàng của tài khoản đang đăng nhập
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "account/order_detail.html",
        order=order
    )
@account_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel_order(order_id):
    if current_user.role != "customer":
        flash("Chức năng này chỉ dành cho khách hàng.", "warning")
        return redirect(url_for("main.home"))

    try:
        # Khóa đơn hàng để tránh xử lý hủy đồng thời.
        order = (
            Order.query
            .filter_by(
                id=order_id,
                user_id=current_user.id
            )
            .with_for_update()
            .first_or_404()
        )

        # Chỉ được hủy khi đang chờ xác nhận.
        if order.order_status != "Chờ xác nhận":
            flash(
                "Không thể hủy đơn hàng ở trạng thái hiện tại.",
                "warning"
            )
            return redirect(
                url_for(
                    "account.order_detail",
                    order_id=order.id
                )
            )

        # Kiểm tra toàn bộ sản phẩm trước khi hoàn kho.
        products_to_restore = []

        for item in order.items:
            product = (
                Product.query
                .filter_by(id=item.product_id)
                .with_for_update()
                .first()
            )

            if product is None:
                raise ValueError(
                    f"Không tìm thấy sản phẩm ID {item.product_id}."
                )

            products_to_restore.append((product, item.quantity))

        # Hoàn kho và cập nhật trạng thái trong cùng giao dịch.
        for product, quantity in products_to_restore:
            product.stock += quantity

        order.order_status = "Đã hủy"

        db.session.commit()

        flash(
            f"Đã hủy đơn hàng {order.order_code} thành công.",
            "success"
        )

    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")

    except Exception:
        db.session.rollback()
        account_bp.logger.exception("Không thể hủy đơn hàng.")
        flash(
            "Có lỗi xảy ra khi hủy đơn hàng. Vui lòng thử lại.",
            "danger"
        )

    return redirect(
        url_for("account.order_detail", order_id=order_id)
    )
from werkzeug.security import check_password_hash, generate_password_hash


@account_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if current_user.role != "customer":
        flash("Chức năng này chỉ dành cho khách hàng.", "warning")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        current_password = request.form.get(
            "current_password", ""
        )
        new_password = request.form.get(
            "new_password", ""
        )
        confirm_password = request.form.get(
            "confirm_password", ""
        )

        # Kiểm tra mật khẩu hiện tại
        if not check_password_hash(
            current_user.password_hash,
            current_password
        ):
            flash("Mật khẩu hiện tại không chính xác.", "danger")
            return render_template("account/change_password.html")

        # Kiểm tra mật khẩu mới
        if len(new_password) < 8:
            flash(
                "Mật khẩu mới phải có ít nhất 8 ký tự.",
                "danger"
            )
            return render_template("account/change_password.html")

        if new_password != confirm_password:
            flash(
                "Mật khẩu xác nhận không khớp.",
                "danger"
            )
            return render_template("account/change_password.html")

        if current_password == new_password:
            flash(
                "Mật khẩu mới phải khác mật khẩu hiện tại.",
                "warning"
            )
            return render_template("account/change_password.html")

        # Mã hóa và lưu mật khẩu mới
        try:
            current_user.password_hash = generate_password_hash(
                new_password
            )
            db.session.commit()

            flash("Đổi mật khẩu thành công.", "success")
            return redirect(url_for("account.profile"))

        except Exception:
            db.session.rollback()
            account_bp.logger.exception(
                "Không thể cập nhật mật khẩu."
            )
            flash(
                "Có lỗi xảy ra khi đổi mật khẩu. Vui lòng thử lại.",
                "danger"
            )

    return render_template("account/change_password.html")
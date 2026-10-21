
"""Các chức năng dành riêng cho nhân viên MENSTYLE."""

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import select

from app.extensions import db
from app.models import Order


employee_bp = Blueprint("employee", __name__, url_prefix="/employee")

ORDERS_PER_PAGE = 10

ORDER_STATUSES = [
    "Chờ xác nhận",
    "Chờ lấy hàng",
    "Đang giao",
    "Đã giao",
    "Hoàn thành",
    "Đã hủy",
]

EMPLOYEE_ORDER_TRANSITIONS = {
    "Chờ xác nhận": {"Chờ lấy hàng"},
    "Chờ lấy hàng": {"Đang giao"},
    "Đang giao": {"Đã giao"},
    "Đã giao": {"Hoàn thành"},
    "Hoàn thành": set(),
    "Đã hủy": set(),
}


def employee_required():
    """Chỉ cho phép nhân viên truy cập khu vực làm việc."""
    if not current_user.is_authenticated:
        abort(403)

    if current_user.role != "employee":
        abort(403)


@employee_bp.route("/")
@login_required
def dashboard():
    """Trang tổng quan nhân viên."""
    employee_required()

    total_orders = Order.query.count()
    
    pending_orders = Order.query.filter_by(
        order_status="Chờ xác nhận"
    ).count()

    shipping_orders = Order.query.filter_by(
        order_status="Đang giao"
    ).count()

    completed_orders = Order.query.filter_by(
        order_status="Hoàn thành"
    ).count()

    return render_template(
        "employee/dashboard.html",
        total_orders=total_orders,
        pending_orders=pending_orders,
        shipping_orders=shipping_orders,
        completed_orders=completed_orders,
    )


@employee_bp.route("/orders")
@login_required
def order_list():
    """Danh sách đơn hàng có tìm kiếm, lọc và phân trang."""
    employee_required()

    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int) or 1

    query = Order.query

    # Tìm theo mã đơn hàng.
    if keyword:
        query = query.filter(Order.order_code.ilike(f"%{keyword}%"))

    # Chỉ lọc theo trạng thái hợp lệ.
    if status in ORDER_STATUSES:
        query = query.filter(Order.order_status == status)
    else:
        status = ""

    # Mỗi trang tối đa 10 đơn hàng.
    pagination = (
        query
        .order_by(Order.created_at.desc())
        .paginate(
            page=page,
            per_page=ORDERS_PER_PAGE,
            error_out=False,
        )
    )

    return render_template(
        "employee/orders.html",
        orders=pagination.items,
        pagination=pagination,
        keyword=keyword,
        selected_status=status,
        order_statuses=ORDER_STATUSES,
    )


@employee_bp.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    """Chi tiết đơn hàng."""
    employee_required()

    order = db.session.get(Order, order_id)

    if order is None:
        abort(404)

    allowed_statuses = sorted(
        EMPLOYEE_ORDER_TRANSITIONS.get(order.order_status, set())
    )

    return render_template(
        "employee/order_detail.html",
        order=order,
        allowed_statuses=allowed_statuses,
    )


@employee_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
def order_update_status(order_id):
    """Cập nhật trạng thái theo quy trình dành cho nhân viên."""
    employee_required()

    order = db.session.get(Order, order_id)

    if order is None:
        abort(404)

    new_status = request.form.get("order_status", "").strip()
    allowed_statuses = EMPLOYEE_ORDER_TRANSITIONS.get(
        order.order_status, set()
    )

    if new_status not in allowed_statuses:
        flash(
            "Trạng thái không hợp lệ hoặc bạn không có quyền thực hiện.",
            "error",
        )
        return redirect(
            url_for("employee.order_detail", order_id=order_id)
        )

    try:
        order.order_status = new_status
        db.session.commit()
        flash("Đã cập nhật trạng thái đơn hàng thành công.", "success")
    except Exception:
        db.session.rollback()
        employee_bp.logger.exception(
            "Không thể cập nhật trạng thái đơn hàng."
        )
        flash(
            "Có lỗi xảy ra khi cập nhật đơn hàng. Vui lòng thử lại.",
            "error",
        )

    return redirect(
        url_for("employee.order_detail", order_id=order_id)
    )

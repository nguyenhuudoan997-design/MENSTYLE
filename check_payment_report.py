
from sqlalchemy import func

from app import create_app
from app.extensions import db
from app.models import Order, Payment


app = create_app()

with app.app_context():
    print("\n===== 1. THỐNG KÊ THANH TOÁN =====")

    payment_stats = (
        db.session.query(
            Payment.payment_status,
            Payment.payment_method,
            func.count(Payment.id).label("so_ban_ghi"),
            func.coalesce(func.sum(Payment.amount), 0).label(
                "tong_tien"
            ),
        )
        .group_by(
            Payment.payment_status,
            Payment.payment_method,
        )
        .order_by(
            Payment.payment_method,
            Payment.payment_status,
        )
        .all()
    )

    if not payment_stats:
        print("Chưa có bản ghi thanh toán.")
    else:
        for row in payment_stats:
            print(
                f"Trạng thái: {row.payment_status} | "
                f"Phương thức: {row.payment_method} | "
                f"Số bản ghi: {row.so_ban_ghi} | "
                f"Tổng tiền: {row.tong_tien:,.0f} đ"
            )

    print("\n===== 2. ĐƠN HÀNG CÓ NHIỀU BẢN GHI THANH TOÁN =====")

    duplicate_stats = (
        db.session.query(
            Payment.order_id,
            func.count(Payment.id).label("so_ban_ghi"),
            func.sum(
                db.case(
                    (Payment.payment_status == "paid", 1),
                    else_=0,
                )
            ).label("so_lan_thanh_toan_thanh_cong"),
            func.coalesce(
                func.sum(
                    db.case(
                        (Payment.payment_status == "paid", Payment.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("tien_da_thanh_toan"),
        )
        .group_by(Payment.order_id)
        .having(
            (func.count(Payment.id) > 1)
            | (
                func.sum(
                    db.case(
                        (Payment.payment_status == "paid", 1),
                        else_=0,
                    )
                ) > 1
            )
        )
        .order_by(Payment.order_id)
        .all()
    )

    if not duplicate_stats:
        print("Không phát hiện đơn hàng có nhiều bản ghi thanh toán.")
    else:
        for row in duplicate_stats:
            print(
                f"Mã ID đơn hàng: {row.order_id} | "
                f"Số bản ghi: {row.so_ban_ghi} | "
                f"Số lần thanh toán thành công: "
                f"{row.so_lan_thanh_toan_thanh_cong} | "
                f"Tổng thanh toán thành công: "
                f"{row.tien_da_thanh_toan:,.0f} đ"
            )

    print("\n===== 3. TỔNG SỐ ĐƠN HÀNG =====")
    print(f"Tổng số đơn hàng: {Order.query.count()}")

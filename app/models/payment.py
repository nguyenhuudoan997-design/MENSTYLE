
from datetime import datetime

from app.extensions import db


class Payment(db.Model):
    """Lưu thông tin thanh toán của đơn hàng."""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    payment_method = db.Column(
        db.String(30), nullable=False, default="COD"
    )
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_status = db.Column(
        db.String(30), nullable=False, default="pending"
    )

    transaction_code = db.Column(db.String(150))
    paid_at = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    order = db.relationship("Order", back_populates="payments")

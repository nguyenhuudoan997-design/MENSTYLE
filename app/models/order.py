
from datetime import datetime

from app.extensions import db


class Order(db.Model):
    """Lưu thông tin đơn hàng của khách hàng."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    order_code = db.Column(db.String(30), unique=True, nullable=False)

    user = db.relationship("User", backref="orders")
    recipient_name = db.Column(db.String(150), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    recipient_email = db.Column(db.String(150))
    shipping_address = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text)

    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    shipping_fee = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    discount_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    payment_method = db.Column(
        db.String(30), nullable=False, default="COD"
    )
    payment_status = db.Column(
        db.String(30), nullable=False, default="pending"
    )
    order_status = db.Column(
        db.String(40), nullable=False, default="Chờ xác nhận"
    )

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    payments = db.relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
    )

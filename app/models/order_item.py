
from datetime import datetime

from app.extensions import db


class OrderItem(db.Model):
    """Lưu các sản phẩm thuộc một đơn hàng."""

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )

    product_name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

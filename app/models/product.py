
"""
app/models/product.py
Model ánh xạ bảng products trong MySQL.
"""

from app.extensions import db


class Product(db.Model):
    """Đại diện cho sản phẩm trong cửa hàng MENSTYLE."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    sale_price = db.Column(db.Numeric(12, 2), nullable=True)
    image = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    material = db.Column(db.String(200), nullable=True)
    sizes = db.Column(db.String(200), nullable=True)
    colors = db.Column(db.String(200), nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    # True: đang kinh doanh; False: ngừng kinh doanh.
    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),
    )

    def __repr__(self):
        return f"<Product {self.id}: {self.name}>"

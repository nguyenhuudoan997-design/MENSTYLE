
from app.extensions import db


class ProductSize(db.Model):
    """Lưu thông số kích thước của từng sản phẩm."""

    __tablename__ = "product_sizes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    size_name = db.Column(db.String(20), nullable=False)

    chest_cm = db.Column(db.Numeric(5, 2), nullable=True)
    waist_cm = db.Column(db.Numeric(5, 2), nullable=True)
    hip_cm = db.Column(db.Numeric(5, 2), nullable=True)
    shoulder_cm = db.Column(db.Numeric(5, 2), nullable=True)
    length_cm = db.Column(db.Numeric(5, 2), nullable=True)

    height_min_cm = db.Column(db.Numeric(5, 2), nullable=True)
    height_max_cm = db.Column(db.Numeric(5, 2), nullable=True)

    weight_min_kg = db.Column(db.Numeric(5, 2), nullable=True)
    weight_max_kg = db.Column(db.Numeric(5, 2), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "product_id",
            "size_name",
            name="uq_product_size",
        ),
    )

    product = db.relationship(
        "Product",
        backref=db.backref("size_charts", lazy=True),
    )

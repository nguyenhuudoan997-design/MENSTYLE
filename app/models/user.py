
"""Model tài khoản người dùng của MENSTYLE."""

from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    """Đại diện cho khách hàng, nhân viên và quản trị viên."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="customer")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    def get_id(self):
        """Trả về ID tài khoản dưới dạng chuỗi."""
        return str(self.id)

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"


"""Model ghi nhật ký hoạt động của hệ thống MENSTYLE."""

from datetime import datetime

from app.extensions import db


class AuditLog(db.Model):
    """Lưu lại lịch sử thao tác của quản trị viên và nhân viên."""

    __tablename__ = "audit_logs"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user_name = db.Column(
        db.String(150),
        nullable=False,
    )

    action = db.Column(
        db.String(30),
        nullable=False,
        index=True,
    )

    target_type = db.Column(
        db.String(50),
        nullable=False,
    )

    target_id = db.Column(
        db.Integer,
        nullable=True,
    )

    description = db.Column(
        db.String(500),
        nullable=False,
    )

    ip_address = db.Column(
        db.String(45),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined",
    )

    def __repr__(self):
        return (
            f"<AuditLog {self.id}: "
            f"{self.action} {self.target_type}>"
        )

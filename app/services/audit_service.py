
"""Các hàm phục vụ ghi nhật ký hoạt động của MENSTYLE."""

from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.audit_log import AuditLog


def log_action(
    action: str,
    target_type: str,
    description: str,
    target_id: int | None = None,
) -> None:
    """Thêm một bản ghi nhật ký vào phiên giao dịch hiện tại."""
    if current_user.is_authenticated:
        user_id = current_user.id
        user_name = current_user.full_name
    else:
        user_id = None
        user_name = "Hệ thống"

    log = AuditLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        target_type=target_type,
        target_id=target_id,
        description=description,
        ip_address=request.remote_addr,
    )

    db.session.add(log)

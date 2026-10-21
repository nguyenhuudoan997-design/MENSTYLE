
"""Tạo bảng audit_logs nếu bảng chưa tồn tại."""

from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.models import AuditLog


def main():
    """Kiểm tra và tạo bảng nhật ký nếu chưa có."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)

        if inspector.has_table(AuditLog.__tablename__):
            print("Bảng audit_logs đã tồn tại. Không cần tạo lại.")
            return

        AuditLog.__table__.create(bind=db.engine)

        print("Đã tạo bảng audit_logs thành công.")
        print("Các bảng dữ liệu hiện có được giữ nguyên.")


if __name__ == "__main__":
    main()

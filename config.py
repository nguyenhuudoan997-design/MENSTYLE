
"""
config.py
Cấu hình ứng dụng MENSTYLE.
Đọc thông tin kết nối từ tệp .env hoặc Environment Variables.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Nạp .env khi chạy cục bộ; trên Render dùng Environment Variables.
load_dotenv(BASE_DIR / ".env")


class Config:
    """Cấu hình chung của ứng dụng Flask."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "Chưa cấu hình SECRET_KEY trong Environment Variables hoặc file .env."
        )

    DB_USER = os.getenv("DB_USER", "menstyle_app")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "mensstyle_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{quote_plus(DB_USER)}:"
        f"{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/"
        f"{DB_NAME}?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chỉ bật SSL khi kết nối đến máy chủ MySQL từ xa.
    if DB_HOST.lower() not in {"localhost", "127.0.0.1"}:
        DB_SSL_CA = Path(
            os.getenv(
                "DB_SSL_CA",
                str(BASE_DIR / "certs" / "ca.pem"),
            )
        )

        if not DB_SSL_CA.is_file():
            raise RuntimeError(
                f"Không tìm thấy chứng chỉ CA: {DB_SSL_CA}. "
                "Hãy đặt file ca.pem trong thư mục certs."
            )

        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "ssl": {
                    "ca": str(DB_SSL_CA),
                }
            }
        }

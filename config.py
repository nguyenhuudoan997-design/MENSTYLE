"""
config.py
Cấu hình ứng dụng MENSTYLE.
Đọc thông tin kết nối từ tệp .env.
"""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Nạp biến môi trường từ tệp .env trong thư mục dự án.
load_dotenv()


class Config:
    """Cấu hình chung của ứng dụng Flask."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "Chưa cấu hình SECRET_KEY trong file .env."
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

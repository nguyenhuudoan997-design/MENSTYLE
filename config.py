
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Đọc .env khi chạy trên máy cá nhân.
# Trên Render, các biến được lấy từ Environment Variables.
load_dotenv(BASE_DIR / ".env")


class Config:
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

    # Bật SSL khi kết nối MySQL từ xa, ví dụ Aiven.
    if DB_HOST.lower() not in {"localhost", "127.0.0.1"}:
        DB_SSL_CA = Path(
            os.getenv("DB_SSL_CA", str(BASE_DIR / "certs" / "ca.pem"))
        )

        if not DB_SSL_CA.is_file():
            raise RuntimeError(
                f"Không tìm thấy chứng chỉ CA: {DB_SSL_CA}"
            )

        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "ssl": {"ca": str(DB_SSL_CA)}
            }
        }

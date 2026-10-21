
"""Khởi tạo các extension dùng chung của ứng dụng."""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

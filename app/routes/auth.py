"""Các route xác thực người dùng."""

import re

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
)
from sqlalchemy import func
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.extensions import db
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def redirect_by_role(user):
    """Chuyển hướng người dùng theo vai trò tài khoản."""
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    if user.role == "employee":
        return redirect(url_for("employee.dashboard"))

    return redirect(url_for("main.home"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Đăng ký tài khoản khách hàng."""
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or len(full_name) > 150:
            flash("Vui lòng nhập họ tên hợp lệ.", "danger")
            return render_template("auth/register.html")

        if (
            not email
            or len(email) > 150
            or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
        ):
            flash("Vui lòng nhập địa chỉ email hợp lệ.", "danger")
            return render_template("auth/register.html")

        if phone and len(phone) > 20:
            flash("Số điện thoại không được vượt quá 20 ký tự.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Mật khẩu phải có ít nhất 8 ký tự.", "danger")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp.", "danger")
            return render_template("auth/register.html")

        existing_user = db.session.scalar(
            db.select(User).where(func.lower(User.email) == email)
        )

        if existing_user:
            flash("Email này đã được đăng ký.", "danger")
            return render_template("auth/register.html")

        user = User(
            full_name=full_name,
            email=email,
            phone=phone or None,
            password_hash=generate_password_hash(password),
            role="customer",
            is_active=True,
        )

        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            auth_bp.logger.exception("Không thể tạo tài khoản khách hàng.")
            flash(
                "Không thể tạo tài khoản lúc này. Vui lòng thử lại.",
                "danger",
            )
            return render_template("auth/register.html")

        login_user(user)
        flash("Đăng ký tài khoản thành công!", "success")
        return redirect(url_for("main.home"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Đăng nhập và chuyển hướng theo vai trò."""
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Vui lòng nhập email và mật khẩu.", "warning")
            return render_template("auth/login.html")

        user = db.session.scalar(
            db.select(User).where(func.lower(User.email) == email)
        )

        if user is None or not check_password_hash(
            user.password_hash,
            password,
        ):
            flash("Email hoặc mật khẩu không chính xác.", "danger")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("Tài khoản của bạn hiện không hoạt động.", "warning")
            return render_template("auth/login.html")

        login_user(user)
        flash("Đăng nhập thành công!", "success")

        return redirect_by_role(user)

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Đăng xuất người dùng hiện tại."""
    logout_user()
    flash("Bạn đã đăng xuất thành công.", "success")
    return redirect(url_for("main.home"))

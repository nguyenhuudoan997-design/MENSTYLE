
"""Khởi tạo ứng dụng Flask MENSTYLE."""

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from config import Config
from app.extensions import db, login_manager


csrf = CSRFProtect()


def create_app():
    """Tạo và cấu hình ứng dụng Flask."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(Config)

    # Khởi tạo bảo vệ CSRF.
    csrf.init_app(app)

    # Khởi tạo cơ sở dữ liệu.
    db.init_app(app)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        from flask_wtf.csrf import CSRFError

        if isinstance(error, CSRFError):
            app.logger.error("CSRF error: %s", error.description)
            return (
                "Lỗi CSRF: " + error.description,
                400,
            )

        return error

    # Khởi tạo đăng nhập.
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."
    login_manager.login_message_category = "warning"

    from app.models import User
  
    @login_manager.user_loader
    def load_user(user_id):
        """Tải người dùng và từ chối tài khoản đã bị khóa."""
        try:
            user = db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

        if user is None or not user.is_active:
            return None

        return user

    # Đăng ký các blueprint.
    from app.routes.main import main_bp
    from app.routes.products import products_bp
    from app.routes.auth import auth_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp
    from app.routes.admin import admin_bp
    from app.routes.employee import employee_bp
    from app.routes.account import account_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(account_bp)

    return app

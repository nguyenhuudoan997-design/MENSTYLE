
"""
app/db_check.py
Kiểm tra kết nối và đọc dữ liệu từ MySQL.
"""

from sqlalchemy import text

from app import create_app
from app.extensions import db
from app.models import Product


def check_database():
    """Kiểm tra kết nối và đọc danh sách sản phẩm."""

    app = create_app()

    with app.app_context():
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT DATABASE()"))
                database_name = result.scalar()

                print(f"Database đang kết nối: {database_name}")

                result = connection.execute(
                    text("""
                        SELECT id, name, price, stock
                        FROM products
                        ORDER BY id
                    """)
                )
                rows = result.fetchall()

                print(f"\nTổng số sản phẩm: {len(rows)}")
                print("-" * 60)

                for row in rows:
                    print(
                        f"ID: {row.id} | "
                        f"Tên: {row.name} | "
                        f"Giá: {row.price:,.0f} VNĐ | "
                        f"Tồn kho: {row.stock}"
                    )

            print("\nKiểm tra bằng SQLAlchemy Product model:")
            model_products = Product.query.order_by(Product.id).all()

            for product in model_products:
                print(
                    f"{product.id} - {product.name} - "
                    f"{product.price:,.0f} VNĐ"
                )

            print("\nKiểm tra database hoàn tất.")

        except Exception as error:
            print("Không thể kết nối hoặc đọc dữ liệu MySQL.")
            print(f"Loại lỗi: {type(error).__name__}")
            print(f"Chi tiết: {error}")


if __name__ == "__main__":
    check_database()

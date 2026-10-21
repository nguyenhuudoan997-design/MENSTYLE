
"""Các route hiển thị sản phẩm ngoài cửa hàng MENSTYLE."""

from flask import Blueprint, render_template, request, abort

from app.models import Product, ProductSize
from app.services.size_recommendation_service import recommend_size

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/products",
)


@products_bp.route("/")
def product_list():
    """Hiển thị, tìm kiếm và lọc sản phẩm đang kinh doanh."""

    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    # Chỉ lấy sản phẩm đang kinh doanh.
    products_query = Product.query.filter_by(is_active=True)

    if query:
        products_query = products_query.filter(
            Product.name.ilike(f"%{query}%")
        )

    if category:
        products_query = products_query.filter(
            Product.category.ilike(f"%{category}%")
        )

    products = products_query.order_by(
        Product.id.desc()
    ).all()

    return render_template(
        "products/list.html",
        products=products,
        query=query,
        category=category,
    )



@products_bp.route("/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):
    """Hiển thị chi tiết và gợi ý size cho sản phẩm đang kinh doanh."""

    product = Product.query.filter_by(
        id=product_id,
        is_active=True,
    ).first_or_404()

    # Chỉ lấy bảng size của sản phẩm đang xem.
    size_charts = ProductSize.query.filter_by(
        product_id=product.id,
    ).order_by(ProductSize.id.asc()).all()

    recommended_size = None
    recommendation_score = 0
    recommendation_message = None

    if request.method == "POST":
        try:
            height = float(request.form.get("height_cm", ""))
            weight = float(request.form.get("weight_kg", ""))

            if not 100 <= height <= 230:
                raise ValueError("Chiều cao phải từ 100 đến 230 cm.")

            if not 20 <= weight <= 250:
                raise ValueError("Cân nặng phải từ 20 đến 250 kg.")

            measurements = {}

            for field in (
                "chest_cm",
                "waist_cm",
                "hip_cm",
                "shoulder_cm",
            ):
                value = request.form.get(field, "").strip()

                if value:
                    number = float(value)

                    if not 20 <= number <= 200:
                        raise ValueError(
                            "Số đo cơ thể phải từ 20 đến 200 cm."
                        )

                    measurements[field] = number
                else:
                    measurements[field] = None

            if not size_charts:
                recommendation_message = (
                    "Sản phẩm chưa có bảng size. "
                    "Vui lòng liên hệ cửa hàng để được tư vấn."
                )
            else:
                recommended_size, recommendation_score = recommend_size(
                    size_charts=size_charts,
                    height_cm=height,
                    weight_kg=weight,
                    **measurements,
                )

                if recommended_size is None:
                    recommendation_message = (
                        "Chưa tìm được size phù hợp với chiều cao "
                        "và cân nặng của bạn. Vui lòng liên hệ cửa hàng."
                    )
                else:
                    recommendation_message = (
                        "Đây là kết quả tham khảo dựa trên bảng size "
                        "của sản phẩm này."
                    )

        except (ValueError, TypeError):
            recommendation_message = (
                "Thông tin chưa hợp lệ. Vui lòng kiểm tra lại "
                "chiều cao, cân nặng và các số đo."
            )

    return render_template(
        "products/detail.html",
        product=product,
        size_charts=size_charts,
        recommended_size=recommended_size,
        recommendation_score=recommendation_score,
        recommendation_message=recommendation_message,
    )


from decimal import Decimal


def recommend_size(
    size_charts,
    height_cm,
    weight_kg,
    chest_cm=None,
    waist_cm=None,
    hip_cm=None,
    shoulder_cm=None,
):
    """
    Đề xuất size dựa trên bảng size của một sản phẩm.

    Trả về:
        (size phù hợp nhất, điểm phù hợp)
        hoặc (None, 0) nếu không có dữ liệu phù hợp.
    """

    if not size_charts:
        return None, 0

    def to_decimal(value):
        if value is None or value == "":
            return None
        return Decimal(str(value))

    height = to_decimal(height_cm)
    weight = to_decimal(weight_kg)

    if height is None or weight is None:
        return None, 0

    measurements = {
        "chest_cm": to_decimal(chest_cm),
        "waist_cm": to_decimal(waist_cm),
        "hip_cm": to_decimal(hip_cm),
        "shoulder_cm": to_decimal(shoulder_cm),
    }

    best_size = None
    best_score = -1

    for size in size_charts:
        score = 0
        checked = 0
        valid = True

        height_min = to_decimal(size.height_min_cm)
        height_max = to_decimal(size.height_max_cm)
        weight_min = to_decimal(size.weight_min_kg)
        weight_max = to_decimal(size.weight_max_kg)

        if height_min is not None and height < height_min:
            valid = False
        if height_max is not None and height > height_max:
            valid = False
        if weight_min is not None and weight < weight_min:
            valid = False
        if weight_max is not None and weight > weight_max:
            valid = False

        if not valid:
            continue

        for field, value in measurements.items():
            if value is None:
                continue

            chart_value = to_decimal(getattr(size, field))

            if chart_value is None:
                continue

            checked += 1

            # Sai lệch không quá 2 cm được xem là gần phù hợp.
            if abs(value - chart_value) <= Decimal("2"):
                score += 1

        if checked > 0:
            score = score / checked

        # Ưu tiên size thỏa khoảng chiều cao và cân nặng.
        # Khi bằng điểm, giữ size đầu tiên trong bảng.
        if score > best_score:
            best_score = score
            best_size = size

    if best_size is None:
        return None, 0

    return best_size, round(best_score * 100)

"""Đối chiếu tên món và kiểm tra ước tính cho 100 g phần ăn được."""

import math

from .core import normalize, normalize_spelling

NUTRIENT_KEYS = ("kcal", "protein", "carb", "fat")


def matching_foods(name, foods):
    def names(food):
        return [food.display_name or food.name] + [alias.alias for alias in food.aliases]

    exact = [
        food
        for food in foods
        if any(normalize_spelling(value) == normalize_spelling(name) for value in names(food))
    ]
    return exact or [
        food for food in foods if any(normalize(value) == normalize(name) for value in names(food))
    ]


def validated_nutrition(values):
    if not isinstance(values, dict):
        raise ValueError("Thiếu số liệu dinh dưỡng")
    result = {}
    for key in NUTRIENT_KEYS:
        value = values.get(key)
        maximum = 900 if key == "kcal" else 100
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0 <= value <= maximum
        ):
            raise ValueError("Số liệu dinh dưỡng ngoài giới hạn cho 100 g")
        result[key] = round(float(value), 4)
    if sum(result[key] for key in ("protein", "carb", "fat")) > 100.05:
        raise ValueError("Tổng protein, carb và chất béo vượt 100 g")
    return result

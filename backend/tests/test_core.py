from types import SimpleNamespace

import pytest

from app.core import fallback_plan, find_avoid_matches, match_foods, nutrition, validate_plan


def food(id, name, kcal=100, tags=None, aliases=None):
    return SimpleNamespace(
        id=id,
        name=name,
        kcal_100g=kcal,
        protein_100g=5,
        carb_100g=10,
        fat_100g=2,
        avoid_tags=tags or [],
        aliases=[SimpleNamespace(alias=a) for a in (aliases or [])],
    )


def test_nutrition_scales_confirmed_mass():
    assert nutrition(food("a", "Món mẫu", 250), 200)["kcal"] == 500


def test_alias_matching_never_invents_id():
    records = [food("FOOD_001", "Phở bò", aliases=["phở tái"])]
    assert [x.id for x in match_foods(["pho tai"], records)] == ["FOOD_001"]
    assert match_foods(["món không có"], records) == []


def test_matching_prefers_exact_vietnamese_spelling():
    records = [food("BEAN", "Đậu đũa"), food("OIL", "Dầu dừa")]
    assert [item.id for item in match_foods(["Đậu đũa"], records)] == ["BEAN"]
    assert [item.id for item in match_foods(["Dầu dừa"], records)] == ["OIL"]


def test_matching_rejects_similar_but_different_dish():
    records = [food("PORK", "Thịt lợn nạc"), food("GRILL", "Thịt nướng")]
    assert match_foods(["Thịt lợn cuộn gia vị"], records) == []


def test_planner_rejects_unknown_and_avoid_tags():
    records = [food("a", "A", tags=["shrimp"]), food("b", "B"), food("c", "C")]
    days = fallback_plan(records, 1800)
    with pytest.raises(ValueError, match="ngoài danh mục"):
        validate_plan(days, ["b", "c"], records, [], 1800)
    with pytest.raises(ValueError, match="cần tránh"):
        validate_plan(days, ["a", "b", "c"], records, ["shrimp"], 1800)


def test_fallback_is_valid_for_allowed_catalog():
    records = [food("a", "A"), food("b", "B", 200), food("c", "C", 150)]
    days = fallback_plan(records, 1800)
    checked = validate_plan(days, ["a", "b", "c"], records, [], 1800)
    assert len(checked) == 7
    assert all(1440 <= day["total_kcal"] <= 2160 for day in checked)


def test_nutrition_uses_catalog_serving_basis():
    serving = food("dish", "Phở gà", 400)
    serving.basis_amount = 1
    serving.basis_unit = "tô"
    assert nutrition(serving, 1)["kcal"] == 400
    assert nutrition(serving, 1.5)["kcal"] == 600


def test_avoidance_matching_understands_meat_without_confusing_accents():
    assert find_avoid_matches(["thịt"], ["Phở gà", "Thịt gà"]) == ["thịt"]
    assert find_avoid_matches(["cá"], ["Sườn sốt cà chua"]) == []

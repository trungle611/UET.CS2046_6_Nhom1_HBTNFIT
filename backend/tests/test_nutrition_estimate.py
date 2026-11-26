from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app import ai
from app.db import Base, get_db
from app.main import app
from app.models import Food, FoodAlias, FoodLog

VALUES = {"kcal": 200, "protein": 15, "carb": 20, "fat": 7}


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'nutrition.db'}")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions() as db:
        for key, name, owner in [
            ("csv", "Món CSV kiểm tra", None),
            ("private", "Món riêng người khác", "other-user"),
        ]:
            food = Food(
                id=key,
                name=name,
                owner_id=owner,
                kcal_100g=500,
                protein_100g=20,
                carb_100g=60,
                fat_100g=10,
                source_type="team_csv",
                source_reference="Test fixture",
                data_version="test",
                basis_amount=1,
                basis_unit="tô",
                basis_label="1 tô",
                is_verified=False,
            )
            if key == "csv":
                food.aliases.append(FoodAlias(alias="Món kiểm tra theo tô"))
            db.add(food)
        db.commit()

    def isolated_db():
        with sessions() as db:
            db.info["user_id"] = "nutrition-test"
            yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, isolated_db)
    client = TestClient(app)  # No global startup: all endpoint data uses the fixture DB.
    yield client, sessions
    client.close()
    engine.dispose()


@pytest.mark.parametrize(
    "name", ["Món CSV kiểm tra", "  mon csv kiem tra  ", "Món kiểm tra theo tô"]
)
def test_catalog_name_or_alias_does_not_call_ai(api_client, monkeypatch, name):
    client, _ = api_client
    monkeypatch.setattr(ai, "estimate_nutrition", lambda *_: pytest.fail("CSV must not call AI"))
    response = client.post("/api/nutrition/estimate", json={"name": name})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "catalog"
    assert body["food"]["basis_unit"] == "tô"
    assert (
        body["food"]["kcal_100g"] == 500
    )  # Keep the actual CSV basis, not a fabricated 100 g conversion.


def test_estimate_only_prefills_and_does_not_create_food_or_log(api_client, monkeypatch):
    client, sessions = api_client
    monkeypatch.setattr(ai, "estimate_nutrition", lambda name: VALUES)
    response = client.post("/api/nutrition/estimate", json={"name": "Pịa Tây Bắc"})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "ai"
    assert body["nutrition_100g"] == VALUES
    assert body["basis_amount"] == 100 and body["basis_unit"] == "g"
    assert body["is_verified"] is False
    with sessions() as db:
        assert db.scalar(select(func.count()).select_from(Food)) == 2
        assert db.scalar(select(func.count()).select_from(FoodLog)) == 0


def test_private_food_from_another_account_is_not_reused(api_client, monkeypatch):
    client, _ = api_client
    calls = []
    monkeypatch.setattr(ai, "estimate_nutrition", lambda name: calls.append(name) or VALUES)
    response = client.post("/api/nutrition/estimate", json={"name": "Món riêng người khác"})
    assert response.json()["source"] == "ai"
    assert calls == ["Món riêng người khác"]


def test_confirmation_scales_100g_estimate_once(api_client, monkeypatch):
    client, _ = api_client
    monkeypatch.setattr(ai, "estimate_nutrition", lambda _: VALUES)
    estimate = client.post("/api/nutrition/estimate", json={"name": "Pịa Tây Bắc"}).json()
    response = client.post(
        "/api/food-logs/batch",
        json={
            "items": [
                {
                    "custom_food": {
                        "name": "Pịa Tây Bắc",
                        **{
                            key + "_100g": value
                            for key, value in estimate["nutrition_100g"].items()
                        },
                    },
                    "grams": 250,
                    "meal_type": "lunch",
                    "confirmed": True,
                }
            ]
        },
    )
    assert response.status_code == 201, response.text
    dashboard = client.get("/api/dashboard").json()
    assert dashboard["totals"]["kcal"] == 500
    assert dashboard["totals"]["protein"] == 37.5


@pytest.mark.parametrize("name", ["", " ", "  ", "x", "x" * 161])
def test_invalid_names_do_not_call_ai(api_client, monkeypatch, name):
    client, _ = api_client
    monkeypatch.setattr(ai, "estimate_nutrition", lambda *_: pytest.fail("Invalid name"))
    assert client.post("/api/nutrition/estimate", json={"name": name}).status_code == 422


@pytest.mark.parametrize("reason", ["timeout", "quota", "overloaded", "authentication"])
def test_service_errors_are_reported_without_saving_food(api_client, monkeypatch, reason):
    client, _ = api_client

    def unavailable(_):
        raise ai.AIServiceError(reason)

    monkeypatch.setattr(ai, "estimate_nutrition", unavailable)
    response = client.post("/api/nutrition/estimate", json={"name": "Pịa Tây Bắc"})
    assert response.status_code == 503
    assert response.json()["detail"] == str(ai.AIServiceError(reason))


def test_unexpected_provider_error_is_not_exposed(api_client, monkeypatch):
    client, _ = api_client

    def broken(_):
        raise RuntimeError("sensitive-provider-key")

    monkeypatch.setattr(ai, "estimate_nutrition", broken)
    response = client.post("/api/nutrition/estimate", json={"name": "Pịa Tây Bắc"})
    assert response.status_code == 503
    assert "sensitive-provider-key" not in response.text


def test_unknown_name_asks_for_more_detail(api_client, monkeypatch):
    client, _ = api_client
    monkeypatch.setattr(ai, "estimate_nutrition", lambda _: None)
    response = client.post("/api/nutrition/estimate", json={"name": "Món quá mơ hồ"})
    assert response.status_code == 422


def test_ai_prompt_uses_100g_and_preserves_valid_values(monkeypatch):
    calls = []
    monkeypatch.setattr(ai, "require_client", lambda: SimpleNamespace())

    def generate(client, prompt, schema):
        calls.append(prompt)
        return {"can_estimate": True, "nutrition_100g": VALUES}

    monkeypatch.setattr(ai, "generate_json", generate)
    assert ai.estimate_nutrition("Pịa Tây Bắc") == VALUES
    assert "đúng 100 g" in calls[0]


@pytest.mark.parametrize(
    "values",
    [
        None,
        [],
        {},
        {**VALUES, "kcal": 901},
        {**VALUES, "fat": -1},
        {**VALUES, "protein": True},
        {**VALUES, "protein": "15"},
        {**VALUES, "kcal": float("nan")},
        {**VALUES, "carb": float("inf")},
        {"kcal": 500, "protein": 50, "carb": 50, "fat": 10},
    ],
)
def test_invalid_model_numbers_are_rejected(monkeypatch, values):
    monkeypatch.setattr(ai, "require_client", lambda: SimpleNamespace())
    monkeypatch.setattr(
        ai, "generate_json", lambda *_: {"can_estimate": True, "nutrition_100g": values}
    )
    with pytest.raises(ai.AIResponseError):
        ai.estimate_nutrition("Pịa Tây Bắc")


@pytest.mark.parametrize("payload", [[], None, {"can_estimate": "true"}, {"can_estimate": True}])
def test_malformed_model_response_is_rejected(monkeypatch, payload):
    monkeypatch.setattr(ai, "require_client", lambda: SimpleNamespace())
    monkeypatch.setattr(ai, "generate_json", lambda *_: payload)
    with pytest.raises(ai.AIResponseError):
        ai.estimate_nutrition("Pịa Tây Bắc")

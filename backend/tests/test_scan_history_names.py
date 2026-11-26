from datetime import datetime, timezone

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Food, FoodLog, ScanHistory

HISTORY_ID = "scan-history-name-test"


@pytest.fixture
def history_client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions() as db:
        db.add(
            Food(
                id="history-csv",
                name="Phở gà",
                kcal_100g=100,
                protein_100g=10,
                carb_100g=10,
                fat_100g=2,
                source_type="team_csv",
                source_reference="Test fixture",
                data_version="test",
                is_verified=False,
            )
        )
        db.add(
            ScanHistory(
                id=HISTORY_ID,
                user_id="history-test",
                image_key="fixture.webp",
                meal_type="lunch",
                status="needs_confirmation",
                result={
                    "dishes": [{"labels": ["Thịt trâu nấu lá lồm"]}, {"labels": ["Món bỏ qua"]}]
                },
            )
        )
        db.commit()

    def isolated_db(request: Request):
        with sessions() as db:
            db.info["user_id"] = request.headers.get("X-Visitor-Id", "history-test")
            yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, isolated_db)
    client = TestClient(app)  # Startup is not run against the global database.
    yield client, sessions
    client.close()
    engine.dispose()


def confirmation(custom=True):
    item = {"grams": 250, "meal_type": "dinner", "confirmed": True}
    if custom:
        item["custom_food"] = {
            "name": "Pịa Tây Bắc",
            "kcal_100g": 200,
            "protein_100g": 15,
            "carb_100g": 20,
            "fat_100g": 7,
        }
    else:
        item["food_id"] = "history-csv"
    return {"confirmation_id": HISTORY_ID, "items": [item]}


@pytest.mark.parametrize("custom,expected", [(True, "Pịa Tây Bắc"), (False, "Phở gà")])
def test_history_uses_confirmed_name_and_preserves_original_ai(history_client, custom, expected):
    client, _ = history_client
    payload = confirmation(custom)
    response = client.post("/api/food-logs/batch", json=payload)
    assert response.status_code == 201, response.text
    record = client.get("/api/scan-history").json()["items"][0]
    assert [dish["name"] for dish in record["confirmed_dishes"]] == [expected]
    assert record["dishes"][0]["labels"] == ["Thịt trâu nấu lá lồm"]
    assert record["meal_type"] == "dinner"
    # The omitted second AI proposal is not in the confirmed list.
    assert len(record["confirmed_dishes"]) == 1
    repeated = client.post("/api/food-logs/batch", json=payload)
    assert repeated.json()["entries"][0]["id"] == response.json()["entries"][0]["id"]


def test_manually_added_extra_dish_is_in_history(history_client):
    client, _ = history_client
    payload = confirmation()
    payload["items"].append(
        {"food_id": "history-csv", "grams": 100, "meal_type": "dinner", "confirmed": True}
    )
    assert client.post("/api/food-logs/batch", json=payload).status_code == 201
    record = client.get("/api/scan-history").json()["items"][0]
    assert [dish["name"] for dish in record["confirmed_dishes"]] == ["Pịa Tây Bắc", "Phở gà"]


def test_old_history_recovers_name_from_original_submission(history_client):
    client, sessions = history_client
    assert client.post("/api/food-logs/batch", json=confirmation()).status_code == 201
    with sessions() as db:
        record = db.get(ScanHistory, HISTORY_ID)
        record.result = {"dishes": record.result["dishes"]}  # Original schema, no snapshot.
        db.commit()
    record = client.get("/api/scan-history").json()["items"][0]
    assert record["confirmed_dishes"][0]["name"] == "Pịa Tây Bắc"
    assert record["dishes"][0]["labels"][0] == "Thịt trâu nấu lá lồm"


def test_new_snapshot_keeps_name_after_food_log_is_deleted(history_client):
    client, sessions = history_client
    created = client.post("/api/food-logs/batch", json=confirmation()).json()["entries"][0]
    with sessions() as db:
        db.delete(db.get(FoodLog, created["id"]))
        db.commit()
    record = client.get("/api/scan-history").json()["items"][0]
    assert record["confirmed_dishes"][0]["name"] == "Pịa Tây Bắc"


def test_missing_legacy_log_does_not_invent_a_confirmed_name(history_client):
    client, sessions = history_client
    created = client.post("/api/food-logs/batch", json=confirmation()).json()["entries"][0]
    with sessions() as db:
        record = db.get(ScanHistory, HISTORY_ID)
        record.result = {"dishes": record.result["dishes"]}
        db.delete(db.get(FoodLog, created["id"]))
        db.commit()
    record = client.get("/api/scan-history").json()["items"][0]
    assert record["confirmed_dishes"] == []
    assert record["dishes"][0]["labels"][0] == "Thịt trâu nấu lá lồm"


def test_confirmed_history_is_not_visible_to_another_account(history_client):
    client, _ = history_client
    assert client.post("/api/food-logs/batch", json=confirmation()).status_code == 201
    assert (
        client.get("/api/scan-history", headers={"X-Visitor-Id": "other-user"}).json()["items"]
        == []
    )


def test_legacy_record_without_submission_does_not_use_ai_as_confirmed_name(history_client):
    client, sessions = history_client
    with sessions() as db:
        db.get(ScanHistory, HISTORY_ID).confirmed_at = datetime.now(timezone.utc)
        db.commit()
    record = client.get("/api/scan-history").json()["items"][0]
    assert record["confirmed_dishes"] is None

import csv

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app import ai, import_foods
from app.core import fallback_plan
from app.main import app
from app.models import Food

from .support import register_account


@pytest.mark.parametrize("provider_available", [True, False])
def test_restored_weekly_plan_is_valid_and_account_scoped(monkeypatch, provider_available):
    def generate(foods, target):
        if not provider_available:
            raise ai.AIConfigurationError("No provider in this test")
        return fallback_plan(foods, target)

    monkeypatch.setattr(ai, "generate_plan", generate)
    with TestClient(app) as client:
        first, second = register_account(client), register_account(client)
        a = {"Authorization": "Bearer " + first["access_token"]}
        b = {"Authorization": "Bearer " + second["access_token"]}
        body = {"week_start": "2027-01-04", "target_kcal": 1800, "avoid_tags": []}
        response = client.post("/api/meal-plans/generate", json=body, headers=a)
        assert response.status_code == 201, response.text
        plan = response.json()
        assert plan["generation_mode"] == ("gemini" if provider_available else "rule_fallback")
        assert len(plan["days"]) == 7
        assert all(
            len(day["meals"]) == 3 and 1440 <= day["total_kcal"] <= 2160 for day in plan["days"]
        )
        path = f"/api/meal-plans/{plan['id']}"
        assert client.get(path, headers=a).status_code == 200
        assert client.get(path, headers=b).status_code == 404
        assert (
            client.post(
                "/api/meal-plans/generate",
                json={**body, "user_id": second["user"]["id"]},
                headers=a,
            ).status_code
            == 422
        )


@pytest.fixture
def importer(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'import.db'}")
    sessions = sessionmaker(bind=engine)
    monkeypatch.setattr(import_foods, "engine", engine)
    monkeypatch.setattr(import_foods, "SessionLocal", sessions)

    def write(rows):
        path = tmp_path / "foods.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=sorted(import_foods.REQUIRED))
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "id": "import-fixture",
                        "name": "Món CSV thử",
                        "kcal_100g": 200,
                        "protein_100g": 10,
                        "carb_100g": 20,
                        "fat_100g": 8,
                        "source_type": "test_fixture",
                        "source_reference": "Synthetic test fixture",
                        "data_version": "test",
                        "is_verified": "false",
                        "avoid_tags": "",
                        "aliases": "Tên thử",
                        **row,
                    }
                )
        return path

    yield sessions, write
    engine.dispose()


def test_restored_importer_preserves_values_and_aliases(importer):
    sessions, write = importer
    assert import_foods.import_csv(write([{}])) == 1
    with sessions() as db:
        food = db.get(Food, "import-fixture")
        assert food.kcal_100g == 200
        assert food.aliases[0].alias == "Tên thử"
        assert food.is_verified is False


def test_import_rejects_nonfinite_data_without_partial_rows(importer):
    sessions, write = importer
    with pytest.raises(ValueError):
        import_foods.import_csv(
            write([{}, {"id": "bad", "name": "Món không hợp lệ", "kcal_100g": "nan"}])
        )
    with sessions() as db:
        assert db.scalars(select(Food)).all() == []

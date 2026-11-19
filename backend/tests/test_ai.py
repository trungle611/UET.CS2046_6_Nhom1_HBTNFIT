import json
from types import SimpleNamespace

import httpx
import pytest

from app import ai


class FakeModels:
    def __init__(self, payloads):
        self.payloads = iter(payloads)
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(text=json.dumps(next(self.payloads), ensure_ascii=False))


def test_scan_requests_per_gram_estimate_for_out_of_catalog_dish(monkeypatch):
    models = FakeModels([{"dishes": [], "warning": ""}])
    monkeypatch.setattr(ai, "client", lambda: SimpleNamespace(models=models))
    ai.scan_image(b"image", "image/jpeg")
    prompt = models.calls[0]["contents"][1]
    assert "ĐÚNG 1 g" in prompt
    assert "MÓN NGOÀI DANH MỤC" in prompt
    schema = models.calls[0]["config"].response_schema
    assert "estimated_nutrition_1g" in schema["properties"]["dishes"]["items"]["required"]


def test_project_fallback_on_quota_error(monkeypatch):
    class QuotaModels:
        def generate_content(self, **kwargs):
            raise ai.errors.ClientError(429, {"error": {"message": "Quota exhausted"}})

    backup = FakeModels([{"ok": True}])
    monkeypatch.setenv("GEMINI_API_KEY", "primary-test-key")
    monkeypatch.setenv("GEMINI_FALLBACK_API_KEY", "backup-test-key")
    monkeypatch.setattr(ai, "client", lambda key=None: SimpleNamespace(models=backup))
    monkeypatch.setattr(ai.time, "sleep", lambda _: None)

    result = ai.generate_json(SimpleNamespace(models=QuotaModels()), "test", {"type": "object"})
    assert result == {"ok": True}
    assert len(backup.calls) == 1


def test_project_fallback_does_not_hide_bad_request(monkeypatch):
    class BadModels:
        def generate_content(self, **kwargs):
            raise ai.errors.ClientError(400, {"error": {"message": "Invalid schema"}})

    monkeypatch.setenv("GEMINI_FALLBACK_API_KEY", "backup-test-key")
    monkeypatch.setattr(ai, "client", lambda key=None: pytest.fail("Must not call backup for 400"))
    with pytest.raises(ai.errors.ClientError):
        ai.generate_json(SimpleNamespace(models=BadModels()), "test", {"type": "object"})


@pytest.mark.parametrize(
    "failure",
    [
        httpx.ReadTimeout("read timeout"),
        httpx.ConnectError("connection failed"),
        ai.errors.ServerError(503, {"error": {"message": "Busy"}}),
    ],
)
def test_transport_and_overload_switch_to_backup(monkeypatch, failure):
    primary_calls = []

    def failed(**kwargs):
        primary_calls.append(kwargs)
        raise failure

    backup = FakeModels([{"ok": True}])
    monkeypatch.setenv("GEMINI_API_KEY", "primary-test")
    monkeypatch.setenv("GEMINI_FALLBACK_API_KEY", "backup-test")
    monkeypatch.setattr(ai, "client", lambda key=None: SimpleNamespace(models=backup))
    monkeypatch.setattr(ai.time, "sleep", lambda _: None)
    result = ai.generate_json(
        SimpleNamespace(models=SimpleNamespace(generate_content=failed)), "test", {"type": "object"}
    )
    assert result == {"ok": True}
    assert len(primary_calls) == 1
    assert len(backup.calls) == 1


def test_network_retry_stops_and_reports_timeout(monkeypatch):
    calls = []

    def failed(**kwargs):
        calls.append(kwargs)
        raise httpx.ReadTimeout("may contain sensitive request details")

    monkeypatch.delenv("GEMINI_FALLBACK_API_KEY", raising=False)
    monkeypatch.setattr(ai.time, "sleep", lambda _: None)
    with pytest.raises(ai.AIServiceError) as caught:
        ai.generate_json(
            SimpleNamespace(models=SimpleNamespace(generate_content=failed)),
            "test",
            {"type": "object"},
        )
    assert caught.value.reason == "timeout"
    assert "sensitive" not in str(caught.value)
    assert len(calls) == ai.MAX_ATTEMPTS


def test_elapsed_budget_prevents_extra_attempt(monkeypatch):
    elapsed = [0.0]
    calls = []

    def failed(**kwargs):
        calls.append(kwargs)
        elapsed[0] = ai.REQUEST_BUDGET_SECONDS + 1
        raise httpx.ReadTimeout("timeout")

    monkeypatch.delenv("GEMINI_FALLBACK_API_KEY", raising=False)
    monkeypatch.setattr(ai.time, "monotonic", lambda: elapsed[0])
    monkeypatch.setattr(ai.time, "sleep", lambda _: None)
    with pytest.raises(ai.AIServiceError, match="phản hồi quá lâu"):
        ai.generate_json(
            SimpleNamespace(models=SimpleNamespace(generate_content=failed)),
            "test",
            {"type": "object"},
        )
    assert len(calls) == 1


def test_language_correction_shares_request_budget(monkeypatch):
    elapsed = [10.0]
    configured_timeouts = []

    def generated(**kwargs):
        configured_timeouts.append(kwargs["config"].http_options.timeout)
        elapsed[0] += 35
        return SimpleNamespace(text="{}")

    monkeypatch.setattr(ai.time, "monotonic", lambda: elapsed[0])
    fake = SimpleNamespace(models=SimpleNamespace(generate_content=generated))

    @ai.bounded_request
    def two_steps():
        ai.generate_json(fake, "scan", {"type": "object"})
        ai.generate_json(fake, "translate", {"type": "object"})

    two_steps()
    assert configured_timeouts == [20000, 10000]
    assert ai._request_deadline.get() is None


def test_scan_retries_translation_when_gemini_returns_english(monkeypatch):
    english = {
        "dishes": [
            {
                "candidate_labels": ["Beef noodle soup"],
                "visible_ingredients": ["Beef slices", "Rice noodles"],
                "uncertainty_reason": "Exact recipe is unclear",
                "estimated_nutrition_100g": {"kcal": 120, "protein": 8, "carb": 15, "fat": 3},
            }
        ],
        "warning": "",
    }
    vietnamese = {
        "dishes": [
            {
                "candidate_labels": ["Phở bò"],
                "visible_ingredients": ["Thịt bò thái lát", "Bánh phở"],
                "uncertainty_reason": "Chưa xác định được công thức chính xác",
                "estimated_nutrition_100g": {"kcal": 120, "protein": 8, "carb": 15, "fat": 3},
            }
        ],
        "warning": "",
    }
    models = FakeModels([english, vietnamese])
    monkeypatch.setattr(ai, "client", lambda: SimpleNamespace(models=models))

    result = ai.scan_image(b"image", "image/jpeg")

    assert result == vietnamese
    assert len(models.calls) == 2
    assert "Dịch toàn bộ" in models.calls[1]["contents"]


def test_scan_rejects_english_after_translation_retry(monkeypatch):
    english = {
        "dishes": [
            {
                "candidate_labels": ["Chicken rice"],
                "visible_ingredients": ["Chicken", "Rice"],
                "uncertainty_reason": "",
                "estimated_nutrition_100g": {"kcal": 150, "protein": 9, "carb": 18, "fat": 4},
            }
        ],
        "warning": "",
    }
    models = FakeModels([english, english])
    monkeypatch.setattr(ai, "client", lambda: SimpleNamespace(models=models))

    with pytest.raises(RuntimeError, match="tiếng Việt"):
        ai.scan_image(b"image", "image/jpeg")


def test_profile_guidance_rewrites_unaccented_vietnamese(monkeypatch):
    unaccented = {
        "summary": "Ban dang co muc tieu tang can va can an du chat dinh duong.",
        "food_options": [
            {
                "title": "Thuc don com va mon man",
                "detail": "Chon mon an phu hop voi muc tieu.",
                "examples": [
                    {"meal_type": "breakfast", "food_id": "F_0332"},
                    {"meal_type": "breakfast", "food_id": "F_0333"},
                    {"meal_type": "lunch", "food_id": "F_0334"},
                    {"meal_type": "lunch", "food_id": "F_0335"},
                    {"meal_type": "dinner", "food_id": "F_0336"},
                    {"meal_type": "dinner", "food_id": "F_0337"},
                ],
            },
            {
                "title": "Thuc don chia nho",
                "detail": "Chia bua an trong ngay de dap ung nang luong.",
                "examples": [
                    {"meal_type": "breakfast", "food_id": "F_0335"},
                    {"meal_type": "breakfast", "food_id": "F_0336"},
                    {"meal_type": "lunch", "food_id": "F_0337"},
                    {"meal_type": "lunch", "food_id": "F_0338"},
                    {"meal_type": "dinner", "food_id": "F_0339"},
                    {"meal_type": "dinner", "food_id": "F_0340"},
                ],
            },
        ],
        "ppl_note": "Phu hop de tap luyen nhieu buoi trong tuan.",
        "ul_note": "Giup tap deu cac nhom co tren va duoi.",
    }
    accented = {
        "summary": "Bạn đang có mục tiêu tăng cân và cần ăn đủ chất dinh dưỡng.",
        "food_options": [
            {
                "title": "Thực đơn cơm và món mặn",
                "detail": "Chọn món ăn phù hợp với mục tiêu.",
                "examples": [
                    {"meal_type": "breakfast", "food_id": "F_0332"},
                    {"meal_type": "breakfast", "food_id": "F_0333"},
                    {"meal_type": "lunch", "food_id": "F_0334"},
                    {"meal_type": "lunch", "food_id": "F_0335"},
                    {"meal_type": "dinner", "food_id": "F_0336"},
                    {"meal_type": "dinner", "food_id": "F_0337"},
                ],
            },
            {
                "title": "Thực đơn chia nhỏ",
                "detail": "Chia bữa ăn trong ngày để đáp ứng năng lượng.",
                "examples": [
                    {"meal_type": "breakfast", "food_id": "F_0335"},
                    {"meal_type": "breakfast", "food_id": "F_0336"},
                    {"meal_type": "lunch", "food_id": "F_0337"},
                    {"meal_type": "lunch", "food_id": "F_0338"},
                    {"meal_type": "dinner", "food_id": "F_0339"},
                    {"meal_type": "dinner", "food_id": "F_0340"},
                ],
            },
        ],
        "ppl_note": "Phù hợp để tập luyện nhiều buổi trong tuần.",
        "ul_note": "Giúp tập đều các nhóm cơ trên và dưới.",
    }
    models = FakeModels([unaccented, accented])
    monkeypatch.setattr(ai, "client", lambda: SimpleNamespace(models=models))
    profile = SimpleNamespace(
        age=22, height_cm=170, weight_kg=60, sex="male", activity_level="moderate", avoid_tags=[]
    )

    result = ai.generate_profile_guidance(profile, 65, ["PPL", "Upper/Lower"])

    assert result == accented
    assert len(models.calls) == 2
    assert "đầy đủ dấu tiếng Việt" in models.calls[1]["contents"]

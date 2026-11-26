"""Thực đơn 7 ngày, cô lập theo tài khoản đăng nhập."""

import os
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import ai
from .core import fallback_plan, nutrition, validate_plan
from .db import get_db
from .models import AiRun, Food, MealPlan, MealPlanItem
from .schemas import PlanIn

router = APIRouter(prefix="/api/meal-plans", tags=["Thực đơn 7 ngày"])


def plan_data(plan):
    days = []
    for day in range(1, 8):
        items = [i for i in plan.items if i.day == day]
        meals = [
            {
                "meal_slot": i.meal_slot,
                "food_id": i.food_id,
                "name": i.food.display_name or i.food.name,
                "grams": i.grams,
                "amount": i.grams,
                "unit": i.food.basis_unit,
                "basis_label": i.food.basis_label,
                "nutrition": nutrition(i.food, i.grams),
                "source_reference": i.food.source_reference,
                "is_verified": i.food.is_verified,
            }
            for i in items
        ]
        days.append(
            {
                "day": day,
                "meals": meals,
                "total_kcal": round(sum(i["nutrition"]["kcal"] for i in meals), 1),
            }
        )
    return {
        "id": plan.id,
        "week_start": plan.week_start,
        "target_kcal": plan.target_kcal,
        "generation_mode": plan.generation_mode,
        "model_version": plan.model_version,
        "days": days,
    }


@router.post("/generate", status_code=201)
def create_plan(payload: PlanIn, db: Session = Depends(get_db)):
    records = db.scalars(
        select(Food).where((Food.owner_id.is_(None)) | (Food.owner_id == db.info["user_id"]))
    ).all()
    allowed = [
        f
        for f in records
        if (
            f.catalog_kind == "dish"
            or f.source_type in {"user_entered", "test_fixture", "demo_synthetic"}
        )
        and f.kcal_100g > 0
        and not (set(f.avoid_tags or []) & set(payload.avoid_tags))
    ]
    if len(allowed) < 3:
        raise HTTPException(422, "Không đủ món phù hợp; cần tối thiểu ba món")
    mode = "gemini"
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    started = perf_counter()
    try:
        proposed = ai.generate_plan(allowed, payload.target_kcal)
        checked = validate_plan(
            proposed, [f.id for f in allowed], records, payload.avoid_tags, payload.target_kcal
        )
        run_status = "ok"
    except Exception:
        mode = "rule_fallback"
        run_status = "fallback"
        model = "deterministic-v1"
        try:
            proposed = fallback_plan(allowed, payload.target_kcal)
            checked = validate_plan(
                proposed, [f.id for f in allowed], records, payload.avoid_tags, payload.target_kcal
            )
        except ValueError as exc:
            raise HTTPException(422, str(exc))
    db.add(
        AiRun(
            user_id=db.info["user_id"],
            purpose="planner",
            prompt_version=ai.PLAN_PROMPT_VERSION,
            model_id=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            latency_ms=round((perf_counter() - started) * 1000),
            status=run_status,
        )
    )
    plan = MealPlan(
        week_start=payload.week_start.isoformat(),
        user_id=db.info["user_id"],
        target_kcal=payload.target_kcal,
        avoid_tags=payload.avoid_tags,
        generation_mode=mode,
        model_version=model,
    )
    for day in checked:
        for meal in day["meals"]:
            plan.items.append(
                MealPlanItem(
                    day=day["day"],
                    meal_slot=meal["meal_slot"],
                    food_id=meal["food_id"],
                    grams=meal["grams"],
                )
            )
    db.add(plan)
    db.commit()
    loaded = db.scalar(
        select(MealPlan)
        .where(MealPlan.id == plan.id)
        .options(selectinload(MealPlan.items).selectinload(MealPlanItem.food))
    )
    return plan_data(loaded)


@router.get("/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.scalar(
        select(MealPlan)
        .where(MealPlan.id == plan_id, MealPlan.user_id == db.info["user_id"])
        .options(selectinload(MealPlan.items).selectinload(MealPlanItem.food))
    )
    if not plan:
        raise HTTPException(404, "Không tìm thấy thực đơn")
    return plan_data(plan)

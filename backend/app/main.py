"""Khởi động database, danh mục CSV và API kiểm tra kết nối."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .catalog import load_catalog
from .db import Base, engine, migrate_demo_columns


@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    migrate_demo_columns()
    load_catalog()
    yield


app = FastAPI(title="HBTNFIT API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "application": "HBTNFIT", "stage": "scaffold"}

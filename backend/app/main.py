import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.data.generate_dummy_dataset import generate_dummy_dataset
from app.data.generate_samples import generate_samples
from app.db import engine
from app.routers import benchmark, predict, samples

app = FastAPI(title="CFA - Car Fluid Analyzer API (dummy)")

# Render 단일 Web Service 배포 시 frontend/dist를 같은 서비스에서 함께 서빙한다.
FRONTEND_DIST = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "dist")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _ensure_dummy_assets():
    generate_dummy_dataset()
    generate_samples()


@app.get("/api/health")
def health():
    db_status = "unconfigured"
    if engine is not None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception:
            db_status = "error"
    return {"status": "ok", "mode": "dummy-data", "db": db_status}


app.include_router(samples.router)
app.include_router(predict.router)
app.include_router(benchmark.router)

# API 라우터 등록 이후에 마운트해야 "/api/*" 요청이 정적 파일 서빙에 가로채이지 않는다.
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

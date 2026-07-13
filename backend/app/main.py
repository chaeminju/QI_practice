from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.data.generate_dummy_dataset import generate_dummy_dataset
from app.data.generate_samples import generate_samples
from app.routers import benchmark, predict, samples

app = FastAPI(title="CFA - Car Fluid Analyzer API (dummy)")

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
    return {"status": "ok", "mode": "dummy-data"}


app.include_router(samples.router)
app.include_router(predict.router)
app.include_router(benchmark.router)

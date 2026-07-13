from fastapi import APIRouter

from app.config import GLOBAL_CD_MAX, GLOBAL_CD_MEAN, GLOBAL_CD_MIN, GLOBAL_CD_STD
from app.data.generate_dummy_dataset import generate_dummy_dataset

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


@router.get("")
def get_benchmark():
    df = generate_dummy_dataset()
    by_type = (
        df.groupby("body_type")["average_cd"]
        .agg(count="count", mean="mean", std="std", min="min", max="max")
        .round(4)
        .reset_index()
        .to_dict(orient="records")
    )
    return {
        "global": {
            "min": GLOBAL_CD_MIN,
            "max": GLOBAL_CD_MAX,
            "mean": GLOBAL_CD_MEAN,
            "std": GLOBAL_CD_STD,
            "count": int(len(df)),
        },
        "by_body_type": by_type,
    }

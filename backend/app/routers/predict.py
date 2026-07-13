import io
import json
import os
from typing import Optional

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import DEFAULT_TARGET_CD
from app.data.generate_samples import SAMPLE_DIR
from app.models import predictor

router = APIRouter(prefix="/api", tags=["predict"])


def _load_sample_meta(sample_id: str) -> dict:
    manifest_path = os.path.join(SAMPLE_DIR, "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    for s in samples:
        if s["id"] == sample_id:
            return s
    raise HTTPException(status_code=404, detail="sample not found")


def _vertices_from_stl_bytes(data: bytes, filename: str) -> np.ndarray:
    try:
        from stl import mesh as stl_mesh

        m = stl_mesh.Mesh.from_file(filename or "upload.stl", fh=io.BytesIO(data))
        return m.vectors.reshape(-1, 3)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"STL 파일을 해석할 수 없습니다: {exc}")


@router.post("/predict")
async def predict(
    file: Optional[UploadFile] = File(default=None),
    sample_id: Optional[str] = Form(default=None),
    target_cd: float = Form(default=DEFAULT_TARGET_CD),
):
    if not file and not sample_id:
        raise HTTPException(status_code=400, detail="file 또는 sample_id 중 하나가 필요합니다")

    if sample_id:
        meta = _load_sample_meta(sample_id)
        stl_path = os.path.join(SAMPLE_DIR, f"{sample_id}.stl")
        with open(stl_path, "rb") as f:
            data = f.read()
        vertices = _vertices_from_stl_bytes(data, f"{sample_id}.stl")
        body_type = meta["body_type"]
        design_id = sample_id
    else:
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="빈 파일입니다")
        vertices = _vertices_from_stl_bytes(data, file.filename or "upload.stl")
        seed = predictor.seed_from_bytes(data)
        features_probe = predictor.extract_geometry_features(vertices)
        body_type = predictor.classify_body_type(features_probe, seed)
        design_id = f"UPLOAD_{seed:016x}"[:20]

    seed = predictor.seed_from_bytes(data)
    features = predictor.extract_geometry_features(vertices)
    cd = predictor.predict_cd(features, body_type, seed)

    result = predictor.summarize_result(design_id, body_type, cd, target_cd, features)
    return result


class ApplyRequest(BaseModel):
    base_cd: float
    body_type: str
    target_cd: float = DEFAULT_TARGET_CD
    recommendation_ids: list[str] = []


@router.post("/apply")
def apply_recommendations(req: ApplyRequest):
    if req.body_type not in predictor.BODY_TYPE_STATS:
        raise HTTPException(status_code=400, detail="알 수 없는 body_type")

    new_cd, delta_sum = predictor.apply_recommendations(req.base_cd, req.recommendation_ids)
    result = predictor.summarize_result(
        design_id="applied",
        body_type=req.body_type,
        cd=new_cd,
        target_cd=req.target_cd,
    )
    result["applied_delta_cd"] = delta_sum
    result["base_cd"] = req.base_cd
    result["applied_recommendation_ids"] = req.recommendation_ids
    return result

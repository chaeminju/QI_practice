import json
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.data.generate_samples import SAMPLE_DIR

router = APIRouter(prefix="/api/samples", tags=["samples"])


@router.get("")
def list_samples():
    manifest_path = os.path.join(SAMPLE_DIR, "manifest.json")
    if not os.path.exists(manifest_path):
        raise HTTPException(status_code=500, detail="sample manifest not found")
    with open(manifest_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    return {"samples": samples}


@router.get("/{sample_id}/file")
def get_sample_file(sample_id: str):
    path = os.path.join(SAMPLE_DIR, f"{sample_id}.stl")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="sample not found")
    return FileResponse(path, media_type="model/stl", filename=f"{sample_id}.stl")

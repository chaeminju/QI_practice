"""
프론트엔드 3D 뷰어 데모용 더미 STL 샘플(세단형/왜건형/쿠페형 실루엣)을 생성한다.
실제 차량 스캔 데이터가 아닌, 차종별 측면 실루엣을 단순화한 목업 지오메트리다.
치수 단위는 미터(m).
"""
import json
import os

from app.data.mesh_utils import extrude_polygon, save_stl

SAMPLE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "sample_data")
)

# 측면 실루엣 (x_frac: 0=전방범퍼 ~ 1=후방범퍼, z_frac: 0=지면 ~ 1=루프)
PROFILES = {
    "Notchback": [
        (0.00, 0.00), (0.00, 0.12), (0.02, 0.22), (0.06, 0.30), (0.22, 0.38),
        (0.30, 0.75), (0.42, 0.95), (0.62, 0.95), (0.68, 0.72), (0.72, 0.55),
        (0.90, 0.50), (0.97, 0.30), (1.00, 0.15), (1.00, 0.00),
    ],
    "Estate": [
        (0.00, 0.00), (0.00, 0.12), (0.02, 0.22), (0.06, 0.30), (0.22, 0.38),
        (0.30, 0.75), (0.42, 0.95), (0.90, 0.95), (0.97, 0.85), (1.00, 0.15),
        (1.00, 0.00),
    ],
    "Fastback": [
        (0.00, 0.00), (0.00, 0.12), (0.02, 0.22), (0.06, 0.30), (0.22, 0.38),
        (0.30, 0.72), (0.42, 0.90), (0.55, 0.88), (0.80, 0.55), (0.95, 0.25),
        (1.00, 0.15), (1.00, 0.00),
    ],
}

SAMPLES = [
    {
        "id": "sample_notchback_01",
        "name": "Sedan Concept A",
        "body_type": "Notchback",
        "length": 4.65,
        "width": 1.82,
        "height": 1.43,
    },
    {
        "id": "sample_estate_01",
        "name": "Wagon Concept B",
        "body_type": "Estate",
        "length": 4.78,
        "width": 1.86,
        "height": 1.48,
    },
    {
        "id": "sample_fastback_01",
        "name": "Coupe Concept C",
        "body_type": "Fastback",
        "length": 4.55,
        "width": 1.88,
        "height": 1.38,
    },
]


def generate_samples(force: bool = False) -> None:
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    manifest_path = os.path.join(SAMPLE_DIR, "manifest.json")

    if os.path.exists(manifest_path) and not force:
        return

    for sample in SAMPLES:
        profile_frac = PROFILES[sample["body_type"]]
        profile = [(fx * sample["length"], fz * sample["height"]) for fx, fz in profile_frac]
        vertices, faces = extrude_polygon(profile, sample["width"])
        # 폭 방향 중앙 정렬 (y=0이 차량 중심이 되도록)
        vertices[:, 1] -= sample["width"] / 2.0
        stl_path = os.path.join(SAMPLE_DIR, f"{sample['id']}.stl")
        save_stl(vertices, faces, stl_path)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLES, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    generate_samples(force=True)
    print(f"generated {len(SAMPLES)} sample STL files -> {SAMPLE_DIR}")

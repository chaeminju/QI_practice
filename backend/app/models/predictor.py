"""
더미(목업) Cd 예측 엔진.

실제 PointNet/RegDGCNN/LightGBM 모델은 학습하지 않는다. 대신 업로드된 STL의
기하 특징(바운딩박스 비율)으로 차종을 휴리스틱 분류하고, 해당 차종의 PRD
통계 분포(평균/표준편차)를 기준으로 파일 해시 시드 기반 재현 가능한 난수를
더해 그럴듯한 Cd 값을 산출한다. 동일 입력은 항상 동일한 예측값을 반환한다.
"""
import hashlib
import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.config import (
    BODY_TYPE_STATS,
    FUEL_SAVINGS_MAX_PCT,
    FUEL_SAVINGS_MIN_PCT,
    GLOBAL_CD_MAX,
    GLOBAL_CD_MIN,
    AVG_ANNUAL_CO2_KG,
    RECOMMENDATIONS,
    MIN_ACHIEVABLE_CD,
)


def seed_from_bytes(data: bytes) -> int:
    digest = hashlib.sha256(data).hexdigest()
    return int(digest[:16], 16)


def extract_geometry_features(vertices: np.ndarray) -> Dict[str, float]:
    """STL 정점 배열(N,3)에서 바운딩박스 기반 더미 형상 특징을 추출한다."""
    xs, ys, zs = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    length = float(xs.max() - xs.min())
    width = float(ys.max() - ys.min())
    height = float(zs.max() - zs.min())
    length = max(length, 1e-6)
    width = max(width, 1e-6)

    frontal_area = width * height * 0.82  # 목업 형상 계수
    aspect_ratio = height / length
    slenderness = length / width

    return {
        "length_m": round(length, 3),
        "width_m": round(width, 3),
        "height_m": round(height, 3),
        "frontal_area_m2": round(frontal_area, 3),
        "aspect_ratio": aspect_ratio,
        "slenderness": slenderness,
    }


def classify_body_type(features: Dict[str, float], seed: int) -> str:
    """바운딩박스 비율 기반 휴리스틱 차종 분류 (실제 판별 모델 아님)."""
    ratio = features["aspect_ratio"]
    rng = random.Random(seed)

    if ratio < 0.28:
        weights = {"Fastback": 0.6, "Estate": 0.25, "Notchback": 0.15}
    elif ratio > 0.34:
        weights = {"Estate": 0.55, "Notchback": 0.35, "Fastback": 0.10}
    else:
        weights = {"Notchback": 0.45, "Fastback": 0.35, "Estate": 0.20}

    body_types = list(weights.keys())
    probs = list(weights.values())
    return rng.choices(body_types, weights=probs, k=1)[0]


def predict_cd(features: Dict[str, float], body_type: str, seed: int) -> float:
    stats = BODY_TYPE_STATS[body_type]
    rng = random.Random(seed)
    noise = rng.gauss(0, stats["std"])

    # 날렵할수록(폭/높이 대비 길이가 길수록) 소폭 개선되는 것처럼 보이는 형상 보정항
    streamline_bonus = _clip((0.32 - features["aspect_ratio"]) * 0.08, -0.015, 0.015)

    cd = stats["mean"] + noise + streamline_bonus
    return round(_clip(cd, GLOBAL_CD_MIN, GLOBAL_CD_MAX), 4)


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _normal_cdf(x: float, mean: float, std: float) -> float:
    if std <= 0:
        return 1.0 if x >= mean else 0.0
    return 0.5 * (1 + math.erf((x - mean) / (std * math.sqrt(2))))


def percentile_better_than(cd: float, body_type: str) -> float:
    """이 Cd 값이 같은 차종 내에서 상위 몇 %(더 낮은 저항)에 속하는지."""
    stats = BODY_TYPE_STATS[body_type]
    better_fraction = 1 - _normal_cdf(cd, stats["mean"], stats["std"])
    return round(_clip(better_fraction * 100, 0.1, 99.9), 1)


def fuel_savings_pct(cd: float) -> float:
    """Alam & Watkins 참고 범위(5~25%)를 전체 Cd 분포에 선형 매핑한 추정치."""
    span = GLOBAL_CD_MAX - GLOBAL_CD_MIN
    ratio = (GLOBAL_CD_MAX - cd) / span
    savings = FUEL_SAVINGS_MIN_PCT + ratio * (FUEL_SAVINGS_MAX_PCT - FUEL_SAVINGS_MIN_PCT)
    return round(_clip(savings, FUEL_SAVINGS_MIN_PCT, FUEL_SAVINGS_MAX_PCT), 1)


def carbon_saved_kg(savings_pct: float) -> float:
    return round(AVG_ANNUAL_CO2_KG * savings_pct / 100, 1)


def build_recommendations(cd: float, target_cd: float) -> List[Dict]:
    needed = cd > target_cd
    ranked = sorted(RECOMMENDATIONS, key=lambda r: r["delta_cd"])  # 개선폭 큰 순
    return [{**r, "needed_to_hit_target": needed} for r in ranked]


def apply_recommendations(
    base_cd: float, recommendation_ids: List[str]
) -> Tuple[float, float]:
    delta_sum = 0.0
    id_set = set(recommendation_ids)
    for rec in RECOMMENDATIONS:
        if rec["id"] in id_set:
            delta_sum += rec["delta_cd"]
    new_cd = _clip(base_cd + delta_sum, MIN_ACHIEVABLE_CD, GLOBAL_CD_MAX)
    return round(new_cd, 4), round(delta_sum, 4)


def summarize_result(
    design_id: str,
    body_type: str,
    cd: float,
    target_cd: float,
    features: Optional[Dict[str, float]] = None,
) -> Dict:
    savings = fuel_savings_pct(cd)
    stats = BODY_TYPE_STATS[body_type]
    return {
        "design_id": design_id,
        "body_type": body_type,
        "cd": cd,
        "target_cd": target_cd,
        "percentile_better_than": percentile_better_than(cd, body_type),
        "fuel_savings_pct": savings,
        "carbon_saved_kg_per_year": carbon_saved_kg(savings),
        "body_type_stats": stats,
        "global_range": {"min": GLOBAL_CD_MIN, "max": GLOBAL_CD_MAX},
        "features": features,
        "recommendations": build_recommendations(cd, target_cd),
    }

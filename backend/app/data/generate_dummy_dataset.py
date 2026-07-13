"""
DrivAerNet++ 데이터셋을 대신하는 더미(합성) 차량 데이터셋 생성기.

실제 9.26GB 포인트클라우드 데이터셋은 다운로드하지 않고, PRD에 기술된
통계 분포(차종별 평균/표준편차/샘플수, 전체 min/max)를 그대로 재현하는
합성 CSV를 만들어 벤치마크 차트와 퍼센타일 계산에 사용한다.
"""
import os

import numpy as np
import pandas as pd

from app.config import BODY_TYPE_STATS, GLOBAL_CD_MIN, GLOBAL_CD_MAX, DUMMY_DATASET_FILENAME

RNG_SEED = 42

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DATA_DIR, DUMMY_DATASET_FILENAME)


def _random_design_params(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """26개 내외의 더미 설계 파라미터를 생성한다 (수치형 23 + 범주형 3 근사)."""
    return pd.DataFrame(
        {
            "length_mm": rng.uniform(4300, 5100, n).round(1),
            "width_mm": rng.uniform(1780, 2020, n).round(1),
            "height_mm": rng.uniform(1360, 1520, n).round(1),
            "wheelbase_mm": rng.uniform(2650, 3050, n).round(1),
            "frontal_area_m2": rng.uniform(2.05, 2.55, n).round(3),
            "ground_clearance_mm": rng.uniform(100, 180, n).round(1),
            "windshield_angle_deg": rng.uniform(24, 34, n).round(1),
            "rear_slant_angle_deg": rng.uniform(10, 45, n).round(1),
            "bumper_curvature_r": rng.uniform(0.05, 0.35, n).round(3),
            "mirror_frontal_area_cm2": rng.uniform(120, 210, n).round(1),
            "underbody_flatness_ratio": rng.uniform(0.4, 0.95, n).round(3),
            "wheel_diameter_mm": rng.uniform(430, 520, n).round(1),
            "greenhouse_taper_ratio": rng.uniform(0.6, 0.95, n).round(3),
            "hood_slope_deg": rng.uniform(4, 16, n).round(1),
            "grille_open_area_pct": rng.uniform(10, 45, n).round(1),
            "roof_length_ratio": rng.uniform(0.3, 0.65, n).round(3),
            "diffuser_angle_deg": rng.uniform(2, 18, n).round(1),
            "side_mirror_type": rng.choice(["conventional", "aero", "camera"], n),
            "spoiler_type": rng.choice(["none", "lip", "wing"], n),
            "wheel_cover_type": rng.choice(["open", "partial", "full"], n),
        }
    )


def generate_dummy_dataset(force: bool = False) -> pd.DataFrame:
    """더미 차량 데이터셋을 생성하고 CSV로 저장한다. 이미 존재하면 재사용."""
    if os.path.exists(CSV_PATH) and not force:
        return pd.read_csv(CSV_PATH)

    rng = np.random.default_rng(RNG_SEED)
    frames = []
    design_counter = 1

    for body_type, stats in BODY_TYPE_STATS.items():
        n = stats["count"]
        cd = rng.normal(stats["mean"], stats["std"], n)
        cd = np.clip(cd, GLOBAL_CD_MIN, GLOBAL_CD_MAX)

        params = _random_design_params(n, rng)
        params.insert(0, "body_type", body_type)
        params.insert(
            0,
            "design_id",
            [f"DUMMY_{body_type[:4].upper()}_{design_counter + i:04d}" for i in range(n)],
        )
        params["average_cd"] = cd.round(4)
        frames.append(params)
        design_counter += n

    df = pd.concat(frames, ignore_index=True)
    df = df.sample(frac=1, random_state=RNG_SEED).reset_index(drop=True)  # shuffle
    df.to_csv(CSV_PATH, index=False)
    return df


if __name__ == "__main__":
    dataset = generate_dummy_dataset(force=True)
    print(f"generated {len(dataset)} dummy rows -> {CSV_PATH}")
    print(dataset.groupby("body_type")["average_cd"].agg(["count", "mean", "std"]))

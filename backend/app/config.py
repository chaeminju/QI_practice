"""
CFA (Car Fluid Analyzer) 더미 데이터 기준 상수.

주의: 이 프로젝트는 실제 DrivAerNet++ 데이터셋(9.26GB)을 사용하지 않는다.
PRD에 명시된 통계 분포(min/max/mean/std, 차종별 평균)를 그대로 목표값으로 삼아
런타임에 더미 데이터셋을 생성하고, 예측값도 규칙 기반 + 랜덤 노이즈로 산출한다.
"""

# 전체 Cd 분포 (PRD 기준)
GLOBAL_CD_MIN = 0.201
GLOBAL_CD_MAX = 0.383
GLOBAL_CD_MEAN = 0.284
GLOBAL_CD_STD = 0.037

# 차종별 통계 (PRD 기준, count는 데모용으로 축소한 값)
BODY_TYPE_STATS = {
    "Notchback": {"mean": 0.247, "std": 0.019, "count": 150},
    "Estate": {"mean": 0.273, "std": 0.019, "count": 180},
    "Fastback": {"mean": 0.296, "std": 0.038, "count": 300},
}

# 연비 절감 참고 문헌 범위 (Alam & Watkins) - 5% ~ 25%
FUEL_SAVINGS_MIN_PCT = 5.0
FUEL_SAVINGS_MAX_PCT = 25.0

# 일반 승용차 연간 평균 탄소 배출량 추정치 (참고용, kg CO2/year)
AVG_ANNUAL_CO2_KG = 4600.0

DUMMY_DATASET_FILENAME = "dummy_vehicles.csv"

RECOMMENDATIONS = [
    {
        "id": "rear_diffuser",
        "title": "리어 디퓨저 40mm 연장",
        "description": "후면 하부 기류를 정리해 후류(wake) 저항을 줄입니다.",
        "category": "후면",
        "delta_cd": -0.014,
    },
    {
        "id": "underbody_cover",
        "title": "언더바디 커버 추가",
        "description": "차체 하부의 난류 발생을 억제해 마찰 저항을 낮춥니다.",
        "category": "하부",
        "delta_cd": -0.011,
    },
    {
        "id": "hood_edge",
        "title": "후드 리딩 엣지 3도 하향",
        "description": "전면 기류 박리 시점을 늦춰 전면 항력을 낮춥니다.",
        "category": "전면",
        "delta_cd": -0.009,
    },
    {
        "id": "roofline",
        "title": "루프라인 후단 5mm 낮추기",
        "description": "후방 박리점을 늦춰 후류 영역 크기를 줄입니다.",
        "category": "상부",
        "delta_cd": -0.008,
    },
    {
        "id": "grille_shutter",
        "title": "액티브 그릴 셔터 (개구율 15% 축소)",
        "description": "불필요한 냉각 기류 유입을 줄여 전면 항력을 낮춥니다.",
        "category": "전면",
        "delta_cd": -0.007,
    },
    {
        "id": "camera_mirror",
        "title": "사이드미러 → 카메라 미러 교체",
        "description": "측면 돌출부를 줄여 미러 후류 와류 발생을 최소화합니다.",
        "category": "측면",
        "delta_cd": -0.006,
    },
]

DEFAULT_TARGET_CD = 0.26

# 예측 후 물리적으로 허용 가능한 최소 Cd (추천 다중 적용 시 하한선)
MIN_ACHIEVABLE_CD = 0.15

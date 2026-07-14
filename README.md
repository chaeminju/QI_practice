# CFA (Car Fluid Analyzer)

자동차 3D 형상(STL)만으로 공기저항 계수(Cd)를 즉시 예측하는 데모 웹 서비스.

> **⚠️ 더미 데이터 모드**: 이 저장소는 실제 DrivAerNet++ 데이터셋(9.26GB)을 사용하지
> 않습니다. PRD에 명시된 통계 분포(차종별 평균/표준편차, 전체 Cd 범위 0.201~0.383)를
> 그대로 재현하는 **합성(더미) 데이터셋**을 백엔드 기동 시 자동 생성하고, 예측값도
> 실제 학습된 PointNet/LightGBM이 아닌 **규칙 기반 + 시드 난수** 로직으로 산출합니다.
> 3D 뷰어에 나오는 샘플 차량 3종도 실제 스캔 데이터가 아닌, 차종(Notchback/Estate/
> Fastback)별 측면 실루엣을 단순화한 목업 지오메트리입니다.

## 구조

```
backend/    FastAPI 서버 (더미 데이터셋 생성 + 예측 API + 프론트엔드 빌드 서빙)
frontend/   React + Vite + three.js 웹 클라이언트
sample_data/  런타임에 자동 생성되는 더미 STL 샘플 (git에는 포함 안 함)
render.yaml   Render 블루프린트 (backend가 frontend 빌드까지 포함해 단일 서비스로 배포)
```

배포 시에는 FastAPI 서버 하나가 `/api/*`는 API로 처리하고, 그 외 경로는
`frontend/dist`에 빌드된 정적 파일(React 앱)을 그대로 서빙합니다. 즉 **Render
Web Service 1개**만 있으면 됩니다(별도 Static Site 서비스 불필요).

## API (backend)

- `GET  /api/health` — 헬스체크
- `GET  /api/samples` — 더미 샘플 차량 목록
- `GET  /api/samples/{id}/file` — 샘플 STL 파일
- `GET  /api/benchmark` — 더미 데이터셋 차종별 통계
- `POST /api/predict` — `file`(STL 업로드) 또는 `sample_id` + `target_cd` → Cd 예측
- `POST /api/apply` — 선택한 디자인 가이드라인 적용 후 재예측

## Render 배포 (Web Service 1개)

이미 만들어둔 Render **Web Service**를 그대로 쓰는 경우, Settings에서 아래처럼
맞춰주면 됩니다 (Root Directory는 비워서 저장소 루트를 그대로 사용합니다).

| 항목 | 값 |
|---|---|
| Root Directory | (비워둠, 저장소 루트) |
| Runtime | Python 3 |
| Build Command | `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build` |
| Start Command | `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT` |

Environment 탭에 환경변수 추가:

| Key | Value |
|---|---|
| `PYTHON_VERSION` | `3.12.7` |
| `VITE_API_BASE` | (빈 값으로 추가) |

`VITE_API_BASE`를 빈 문자열로 두면 프론트엔드가 같은 오리진의 `/api/...` 상대경로로
호출하도록 빌드됩니다(백엔드가 프론트엔드를 같은 서비스에서 서빙하므로 별도 도메인이
필요 없습니다).

설정을 저장하면 **Manual Deploy**로 재배포하세요. 첫 기동 시 더미 데이터셋(CSV)과
샘플 STL이 자동 생성됩니다(코드에 시드 고정되어 있어 항상 같은 값 재현).

처음부터 새로 만든다면 "New +" → "Blueprint"로 이 저장소를 연결해도 `render.yaml`이
동일한 설정으로 서비스 1개를 자동 생성합니다.

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
backend/    FastAPI 서버 (더미 데이터셋 생성 + 예측 API)
frontend/   React + Vite + three.js 웹 클라이언트
sample_data/  런타임에 자동 생성되는 더미 STL 샘플 (git에는 포함 안 함)
render.yaml   Render 블루프린트 (backend/frontend 두 서비스 동시 배포)
```

## API (backend)

- `GET  /api/health` — 헬스체크
- `GET  /api/samples` — 더미 샘플 차량 목록
- `GET  /api/samples/{id}/file` — 샘플 STL 파일
- `GET  /api/benchmark` — 더미 데이터셋 차종별 통계
- `POST /api/predict` — `file`(STL 업로드) 또는 `sample_id` + `target_cd` → Cd 예측
- `POST /api/apply` — 선택한 디자인 가이드라인 적용 후 재예측

## Render 배포

1. GitHub에 푸시된 이 저장소를 Render에 연결합니다 (New → Blueprint).
2. 저장소 루트의 `render.yaml`을 인식하면 `cfa-backend`(Python 웹 서비스)와
   `cfa-frontend`(정적 사이트) 두 개가 함께 생성됩니다.
3. `cfa-frontend`의 `VITE_API_BASE` 환경변수는 `cfa-backend`의 호스트를 자동
   참조하도록 설정되어 있으므로 별도 입력이 필요 없습니다.
4. 배포 후 `cfa-backend`가 최초 기동될 때 더미 데이터셋(CSV)과 샘플 STL이
   자동 생성됩니다(코드에 시드 고정되어 있어 항상 같은 값 재현).

블루프린트를 쓰지 않고 수동으로 두 서비스를 만들 경우:

- **backend**: Root Directory `backend`, Build `pip install -r requirements.txt`,
  Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **frontend**: Root Directory `frontend`, Build `npm install && npm run build`,
  Publish Directory `dist`, 환경변수 `VITE_API_BASE=https://<backend-service>.onrender.com`

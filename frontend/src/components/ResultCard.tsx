import type { PredictResult } from '../api/types'

interface ResultCardProps {
  result: PredictResult
}

function clampPct(value: number, min: number, max: number): number {
  return Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100))
}

export default function ResultCard({ result }: ResultCardProps) {
  const { global_range, cd, target_cd, body_type, percentile_better_than } = result
  const cdPos = clampPct(cd, global_range.min, global_range.max)
  const targetPos = clampPct(target_cd, global_range.min, global_range.max)
  const meetsTarget = cd <= target_cd

  return (
    <div className="panel">
      <h2>2. 예측 결과 (더미 모델)</h2>

      <div className="cd-headline">
        <span className="cd-value">{cd.toFixed(3)}</span>
        <span className="cd-unit">Cd</span>
        <span className={`badge ${meetsTarget ? 'badge-good' : 'badge-warn'}`}>
          {body_type} · {meetsTarget ? '목표 달성' : '목표 초과'}
        </span>
      </div>

      <div className="gauge">
        <div className="gauge-track">
          <div className="gauge-fill" style={{ width: `${cdPos}%` }} />
          <div className="gauge-target-marker" style={{ left: `${targetPos}%` }} title="목표 Cd" />
        </div>
        <div className="gauge-labels">
          <span>{global_range.min.toFixed(3)} (최저 저항)</span>
          <span>{global_range.max.toFixed(3)} (최고 저항)</span>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat">
          <span className="stat-label">차종 내 순위</span>
          <span className="stat-value">상위 {percentile_better_than}%</span>
        </div>
        <div className="stat">
          <span className="stat-label">예상 연비 절감</span>
          <span className="stat-value">{result.fuel_savings_pct}%</span>
        </div>
        <div className="stat">
          <span className="stat-label">예상 탄소 절감</span>
          <span className="stat-value">{result.carbon_saved_kg_per_year} kg/년</span>
        </div>
      </div>

      {result.features && (
        <div className="feature-row">
          <span>길이 {result.features.length_m} m</span>
          <span>폭 {result.features.width_m} m</span>
          <span>높이 {result.features.height_m} m</span>
          <span>전면 투영면적 {result.features.frontal_area_m2} m²</span>
        </div>
      )}

      <p className="disclaimer">
        * 더미 데이터 기반 규칙 예측치이며, 실제 CFD 결과가 아닙니다. 연비/탄소 절감치는 Alam
        &amp; Watkins(5~25%) 참고 문헌 범위를 전체 Cd 분포에 선형 매핑한 참고용 추정입니다.
      </p>
    </div>
  )
}

import { useState } from 'react'
import type { Recommendation } from '../api/types'

interface RecommendationListProps {
  recommendations: Recommendation[]
  onApply: (selectedIds: string[]) => void
  applying: boolean
}

export default function RecommendationList({
  recommendations,
  onApply,
  applying,
}: RecommendationListProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const totalDelta = recommendations
    .filter((r) => selected.has(r.id))
    .reduce((sum, r) => sum + r.delta_cd, 0)

  return (
    <div className="panel">
      <h2>4. 디자인 수정 가이드라인</h2>
      <p className="hint">개선 효과가 큰 순서로 정렬되어 있습니다. 적용할 항목을 선택하세요.</p>

      <ul className="rec-list">
        {recommendations.map((rec) => (
          <li key={rec.id} className={`rec-item ${selected.has(rec.id) ? 'active' : ''}`}>
            <label>
              <input
                type="checkbox"
                checked={selected.has(rec.id)}
                onChange={() => toggle(rec.id)}
              />
              <div className="rec-text">
                <span className="rec-title">
                  {rec.title} <span className="rec-tag">{rec.category}</span>
                </span>
                <span className="rec-desc">{rec.description}</span>
              </div>
              <span className="rec-delta">{rec.delta_cd.toFixed(3)}</span>
            </label>
          </li>
        ))}
      </ul>

      <div className="apply-row">
        <span>선택 항목 예상 개선폭: {totalDelta.toFixed(3)}</span>
        <button
          className="primary-btn"
          disabled={selected.size === 0 || applying}
          onClick={() => onApply(Array.from(selected))}
        >
          {applying ? '재계산 중…' : '적용 후 재예측'}
        </button>
      </div>
    </div>
  )
}

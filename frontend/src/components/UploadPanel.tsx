import { useRef } from 'react'
import type { SampleMeta } from '../api/types'

interface UploadPanelProps {
  samples: SampleMeta[]
  selectedSampleId: string | null
  onSelectSample: (id: string) => void
  onSelectFile: (file: File) => void
  targetCd: number
  onTargetCdChange: (value: number) => void
  onPredict: () => void
  loading: boolean
}

export default function UploadPanel({
  samples,
  selectedSampleId,
  onSelectSample,
  onSelectFile,
  targetCd,
  onTargetCdChange,
  onPredict,
  loading,
}: UploadPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  return (
    <div className="panel">
      <h2>1. 차량 형상 선택</h2>
      <p className="hint">더미 샘플 차량을 고르거나, 직접 STL 파일을 업로드하세요.</p>

      <div className="sample-grid">
        {samples.map((s) => (
          <button
            key={s.id}
            className={`sample-card ${selectedSampleId === s.id ? 'active' : ''}`}
            onClick={() => onSelectSample(s.id)}
          >
            <span className="sample-name">{s.name}</span>
            <span className="sample-type">{s.body_type}</span>
          </button>
        ))}
      </div>

      <div className="upload-row">
        <button
          className="secondary-btn"
          onClick={() => fileInputRef.current?.click()}
        >
          내 STL 파일 업로드
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".stl"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) onSelectFile(file)
            e.target.value = ''
          }}
        />
      </div>

      <div className="target-row">
        <label htmlFor="target-cd">
          목표 Cd: <strong>{targetCd.toFixed(3)}</strong>
        </label>
        <input
          id="target-cd"
          type="range"
          min={0.2}
          max={0.38}
          step={0.005}
          value={targetCd}
          onChange={(e) => onTargetCdChange(Number(e.target.value))}
        />
      </div>

      <button className="primary-btn" onClick={onPredict} disabled={loading}>
        {loading ? '예측 중…' : 'Cd 예측하기'}
      </button>
    </div>
  )
}

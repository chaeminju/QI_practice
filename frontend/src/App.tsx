import { useEffect, useState } from 'react'
import {
  applyRecommendations,
  fetchBenchmark,
  fetchSamples,
  predictFromFile,
  predictFromSample,
  sampleFileUrl,
} from './api/client'
import type { BenchmarkResponse, PredictResult, SampleMeta } from './api/types'
import Viewer3D, { type MeshSource } from './components/Viewer3D'
import UploadPanel from './components/UploadPanel'
import ResultCard from './components/ResultCard'
import BenchmarkChart from './components/BenchmarkChart'
import RecommendationList from './components/RecommendationList'

export default function App() {
  const [samples, setSamples] = useState<SampleMeta[]>([])
  const [benchmark, setBenchmark] = useState<BenchmarkResponse | null>(null)
  const [selectedSampleId, setSelectedSampleId] = useState<string | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [meshSource, setMeshSource] = useState<MeshSource | null>(null)
  const [targetCd, setTargetCd] = useState(0.26)
  const [result, setResult] = useState<PredictResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [applying, setApplying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSamples()
      .then((list) => {
        setSamples(list)
        if (list.length > 0) {
          setSelectedSampleId(list[0].id)
          setMeshSource({ kind: 'url', url: sampleFileUrl(list[0].id) })
        }
      })
      .catch((e) => setError(String(e.message ?? e)))

    fetchBenchmark()
      .then(setBenchmark)
      .catch((e) => setError(String(e.message ?? e)))
  }, [])

  const handleSelectSample = (id: string) => {
    setSelectedSampleId(id)
    setUploadedFile(null)
    setMeshSource({ kind: 'url', url: sampleFileUrl(id) })
    setResult(null)
    setError(null)
  }

  const handleSelectFile = (file: File) => {
    setUploadedFile(file)
    setSelectedSampleId(null)
    setResult(null)
    setError(null)
    file
      .arrayBuffer()
      .then((buffer) => setMeshSource({ kind: 'buffer', buffer }))
      .catch((e) => setError(String(e.message ?? e)))
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      let res: PredictResult
      if (uploadedFile) {
        res = await predictFromFile(uploadedFile, targetCd)
      } else if (selectedSampleId) {
        res = await predictFromSample(selectedSampleId, targetCd)
      } else {
        throw new Error('샘플을 선택하거나 STL 파일을 업로드하세요')
      }
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async (ids: string[]) => {
    if (!result) return
    setApplying(true)
    setError(null)
    try {
      const res = await applyRecommendations(result.cd, result.body_type, targetCd, ids)
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">CFA</span>
          <span className="brand-sub">Car Fluid Analyzer · Instant Aerodynamic Drag Prediction</span>
        </div>
        <span className="mode-badge">DUMMY DATA MODE</span>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main className="app-grid">
        <section className="viewer-col">
          <div className="viewer-box">
            <Viewer3D source={meshSource} />
          </div>
          <UploadPanel
            samples={samples}
            selectedSampleId={selectedSampleId}
            onSelectSample={handleSelectSample}
            onSelectFile={handleSelectFile}
            targetCd={targetCd}
            onTargetCdChange={setTargetCd}
            onPredict={handlePredict}
            loading={loading}
          />
        </section>

        <section className="result-col">
          {result ? (
            <>
              <ResultCard result={result} />
              <BenchmarkChart
                benchmark={benchmark}
                currentBodyType={result.body_type}
                currentCd={result.cd}
              />
              <RecommendationList
                recommendations={result.recommendations}
                onApply={handleApply}
                applying={applying}
              />
            </>
          ) : (
            <div className="panel placeholder-panel">
              <h2>결과 대기 중</h2>
              <p className="hint">
                왼쪽에서 차량 형상을 선택하고 &ldquo;Cd 예측하기&rdquo; 버튼을 눌러주세요.
              </p>
              <BenchmarkChart benchmark={benchmark} />
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

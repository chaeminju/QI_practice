import type { BenchmarkResponse, PredictResult, SampleMeta } from './types'

// 배포 시(Render 단일 Web Service)는 FastAPI가 프론트엔드 빌드를 같은 오리진에서
// 서빙하므로 VITE_API_BASE=""(빈 문자열)로 두면 상대경로("/api/...")로 호출된다.
// 로컬 개발(frontend 5173 / backend 8000 분리 실행)에서는 env 미설정 시 localhost로 fallback.
const rawBase = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const API_BASE = rawBase === '' || rawBase.startsWith('http') ? rawBase : `https://${rawBase}`

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || `요청 실패 (${res.status})`)
  }
  return res.json() as Promise<T>
}

export async function fetchSamples(): Promise<SampleMeta[]> {
  const res = await fetch(`${API_BASE}/api/samples`)
  const data = await handle<{ samples: SampleMeta[] }>(res)
  return data.samples
}

export function sampleFileUrl(sampleId: string): string {
  return `${API_BASE}/api/samples/${sampleId}/file`
}

export async function fetchBenchmark(): Promise<BenchmarkResponse> {
  const res = await fetch(`${API_BASE}/api/benchmark`)
  return handle<BenchmarkResponse>(res)
}

export async function predictFromSample(
  sampleId: string,
  targetCd: number,
): Promise<PredictResult> {
  const form = new FormData()
  form.set('sample_id', sampleId)
  form.set('target_cd', String(targetCd))
  const res = await fetch(`${API_BASE}/api/predict`, { method: 'POST', body: form })
  return handle<PredictResult>(res)
}

export async function predictFromFile(file: File, targetCd: number): Promise<PredictResult> {
  const form = new FormData()
  form.set('file', file)
  form.set('target_cd', String(targetCd))
  const res = await fetch(`${API_BASE}/api/predict`, { method: 'POST', body: form })
  return handle<PredictResult>(res)
}

export async function applyRecommendations(
  baseCd: number,
  bodyType: string,
  targetCd: number,
  recommendationIds: string[],
): Promise<PredictResult> {
  const res = await fetch(`${API_BASE}/api/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      base_cd: baseCd,
      body_type: bodyType,
      target_cd: targetCd,
      recommendation_ids: recommendationIds,
    }),
  })
  return handle<PredictResult>(res)
}

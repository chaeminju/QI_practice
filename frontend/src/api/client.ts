import type { BenchmarkResponse, PredictResult, SampleMeta } from './types'

const rawBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
// Render 블루프린트의 fromService(property: host)는 스킴 없는 호스트만 넘겨주므로 보정한다.
const API_BASE = rawBase.startsWith('http') ? rawBase : `https://${rawBase}`

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

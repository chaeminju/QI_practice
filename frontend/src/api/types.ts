export interface SampleMeta {
  id: string
  name: string
  body_type: string
  length: number
  width: number
  height: number
}

export interface Recommendation {
  id: string
  title: string
  description: string
  category: string
  delta_cd: number
  needed_to_hit_target: boolean
}

export interface BodyTypeStats {
  mean: number
  std: number
  count: number
}

export interface PredictResult {
  design_id: string
  body_type: string
  cd: number
  target_cd: number
  percentile_better_than: number
  fuel_savings_pct: number
  carbon_saved_kg_per_year: number
  body_type_stats: BodyTypeStats
  global_range: { min: number; max: number }
  features: Record<string, number> | null
  recommendations: Recommendation[]
  applied_delta_cd?: number
  base_cd?: number
  applied_recommendation_ids?: string[]
}

export interface BenchmarkByType {
  body_type: string
  count: number
  mean: number
  std: number
  min: number
  max: number
}

export interface BenchmarkResponse {
  global: { min: number; max: number; mean: number; std: number; count: number }
  by_body_type: BenchmarkByType[]
}

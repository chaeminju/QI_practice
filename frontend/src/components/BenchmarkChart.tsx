import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { BenchmarkResponse } from '../api/types'

interface BenchmarkChartProps {
  benchmark: BenchmarkResponse | null
  currentBodyType?: string
  currentCd?: number
}

const COLORS: Record<string, string> = {
  Notchback: '#38bdf8',
  Estate: '#34d399',
  Fastback: '#fb923c',
}

export default function BenchmarkChart({
  benchmark,
  currentBodyType,
  currentCd,
}: BenchmarkChartProps) {
  if (!benchmark) return null

  const data = benchmark.by_body_type.map((row) => ({
    body_type: row.body_type,
    mean: row.mean,
    isCurrent: row.body_type === currentBodyType,
  }))

  return (
    <div className="panel">
      <h2>3. 차종별 벤치마크 (더미 데이터셋)</h2>
      <p className="hint">
        더미 데이터셋 {benchmark.global.count}개 샘플 기준 차종별 평균 Cd. 붉은 점선은 현재 예측
        Cd 값입니다.
      </p>
      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 8, right: 16, left: -12, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="body_type" stroke="#94a3b8" fontSize={12} />
            <YAxis domain={[0.2, 0.4]} stroke="#94a3b8" fontSize={12} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155' }}
              formatter={(value: number) => value.toFixed(3)}
            />
            <Bar dataKey="mean" radius={[6, 6, 0, 0]}>
              {data.map((row) => (
                <Cell
                  key={row.body_type}
                  fill={COLORS[row.body_type] ?? '#64748b'}
                  stroke={row.isCurrent ? '#f8fafc' : 'none'}
                  strokeWidth={row.isCurrent ? 2 : 0}
                />
              ))}
            </Bar>
            {currentCd != null && (
              <ReferenceLine
                y={currentCd}
                stroke="#f87171"
                strokeDasharray="4 4"
                label={{ value: `현재 ${currentCd.toFixed(3)}`, fill: '#f87171', fontSize: 12 }}
              />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

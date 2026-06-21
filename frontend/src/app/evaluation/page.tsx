'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { RefreshCw } from 'lucide-react'

interface Metrics {
  precision: number
  recall: number
  f1_score: number
}

interface EvaluationData {
  overall: Metrics
  by_severity: Record<string, Metrics>
  by_label: Record<string, Metrics>
  confusion_matrix: { labels: string[]; matrix: number[][] }
  computed_at: string
}

export default function EvaluationPage() {
  const [data, setData] = useState<EvaluationData | null>(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get<{ data: EvaluationData }>('/evaluation/metrics')
      .then(res => setData(res.data))
      .finally(() => setLoading(false))
  }

  const runEval = async () => {
    setLoading(true)
    await api.post('/evaluation/run')
    load()
  }

  useEffect(() => { load() }, [])

  if (loading && !data) {
    return <div className="animate-pulse space-y-4">
      <div className="h-8 w-64 bg-gray-200 rounded" />
      <div className="h-32 bg-gray-200 rounded" />
    </div>
  }

  const d = data!

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Evaluation Dashboard</h1>
          <p className="text-gray-500 mt-1">Anomaly detection performance metrics</p>
        </div>
        <button onClick={runEval} disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 text-sm font-medium disabled:opacity-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Run Evaluation
        </button>
      </div>

      {/* Overall KPI */}
      <div className="grid grid-cols-3 gap-4">
        <MetricCard label="Critical Recall" value={d.overall.recall} color="text-green-700" bg="bg-green-50" />
        <MetricCard label="Precision" value={d.overall.precision} color="text-blue-700" bg="bg-blue-50" />
        <MetricCard label="F1 Score" value={d.overall.f1_score} color="text-purple-700" bg="bg-purple-50" />
      </div>

      {/* By Severity */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">By Severity</h3>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Severity</th>
              <th className="text-right px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Precision</th>
              <th className="text-right px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Recall</th>
              <th className="text-right px-3 py-2 text-xs font-semibold text-gray-500 uppercase">F1</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(d.by_severity).map(([sev, m]) => (
              <tr key={sev} className="border-b border-gray-100">
                <td className="px-3 py-2 font-medium">{sev}</td>
                <td className="px-3 py-2 text-right">{(m.precision * 100).toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{(m.recall * 100).toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{(m.f1_score * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* By Label */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">By Anomaly Label</h3>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Label</th>
              <th className="text-right px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Precision</th>
              <th className="text-right px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Recall</th>
              <th className="text-right px-3 py-2 text-xs font-semibold text-gray-500 uppercase">F1</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(d.by_label).map(([label, m]) => (
              <tr key={label} className="border-b border-gray-100">
                <td className="px-3 py-2 font-mono text-xs">{label}</td>
                <td className="px-3 py-2 text-right">{(m.precision * 100).toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{(m.recall * 100).toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{(m.f1_score * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {d.computed_at && (
        <p className="text-xs text-gray-400">Last computed: {new Date(d.computed_at).toLocaleString()}</p>
      )}
    </div>
  )
}

function MetricCard({ label, value, color, bg }: { label: string; value: number; color: string; bg: string }) {
  return (
    <div className={`${bg} rounded-xl border border-gray-200 p-4 text-center`}>
      <div className={`text-3xl font-bold ${color}`}>{(value * 100).toFixed(0)}%</div>
      <div className="text-xs text-gray-600 mt-1 font-medium">{label}</div>
    </div>
  )
}

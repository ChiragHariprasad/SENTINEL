'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { riskTextColor, riskColor } from '@/lib/utils'
import { AlertTriangle, Search } from 'lucide-react'

interface Anomaly {
  anomaly_id: string
  vendor_id: string
  rule_name: string
  severity: string
  description: string
  detected_at: string
  status: string
  vendor_name?: string
}

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.get<{ data: { total: number; items: Anomaly[] } }>('/anomalies')
      .then(res => setAnomalies(res.data.items))
      .finally(() => setLoading(false))
  }, [])

  const filtered = anomalies.filter(a =>
    !search || a.rule_name.toLowerCase().includes(search.toLowerCase()) ||
    a.description.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-sentinel-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Anomaly Center</h1>
            <p className="text-gray-500 mt-1">Detected anomalies across vendor registry</p>
          </div>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text" placeholder="Search anomalies..."
          value={search} onChange={e => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500"
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Rule</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Description</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Severity</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Detected</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">Loading...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">No anomalies found</td></tr>
            ) : filtered.map(a => (
              <tr key={a.anomaly_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{a.rule_name}</td>
                <td className="px-4 py-3 text-gray-600 max-w-md truncate">{a.description}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    a.severity === 'CRITICAL' ? 'bg-red-50 text-risk-red' :
                    a.severity === 'HIGH' ? 'bg-orange-50 text-orange-700' :
                    'bg-yellow-50 text-risk-yellow'
                  }`}>{a.severity}</span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    a.status === 'OPEN' ? 'bg-red-50 text-risk-red' :
                    a.status === 'RESOLVED' ? 'bg-green-50 text-risk-green' :
                    'bg-gray-50 text-gray-600'
                  }`}>{a.status}</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-500 text-sm">{new Date(a.detected_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

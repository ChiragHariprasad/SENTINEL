'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { Bell, CheckCircle } from 'lucide-react'

interface Alert {
  alert_id: string
  vendor_id: string
  title: string
  severity: string
  status: string
  created_at: string
  vendor_name?: string
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<{ data: { total: number; items: Alert[] } }>('/alerts')
      .then(res => setAlerts(res.data.items))
      .finally(() => setLoading(false))
  }, [])

  const resolve = async (id: string) => {
    await api.post(`/alerts/${id}/resolve`, {})
    setAlerts(prev => prev.map(a => a.alert_id === id ? { ...a, status: 'RESOLVED' } : a))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Bell className="w-6 h-6 text-sentinel-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-500 mt-1">Actionable alerts and notifications</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Title</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Severity</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Created</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">Loading...</td></tr>
            ) : alerts.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">No alerts</td></tr>
            ) : alerts.map(a => (
              <tr key={a.alert_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{a.title}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    a.severity === 'CRITICAL' ? 'bg-red-50 text-risk-red' :
                    a.severity === 'HIGH' ? 'bg-orange-50 text-orange-700' :
                    'bg-yellow-50 text-risk-yellow'
                  }`}>{a.severity}</span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    a.status === 'OPEN' ? 'bg-red-50 text-risk-red' : 'bg-green-50 text-risk-green'
                  }`}>{a.status}</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-500 text-sm">{new Date(a.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3 text-right">
                  {a.status === 'OPEN' && (
                    <button onClick={() => resolve(a.alert_id)}
                      className="text-sentinel-600 hover:text-sentinel-800 text-sm font-medium flex items-center gap-1 ml-auto">
                      <CheckCircle className="w-4 h-4" /> Resolve
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { riskTextColor, riskColor } from '@/lib/utils'
import { Shield } from 'lucide-react'

interface VendorRisk {
  vendor_id: string
  vendor_name: string
  overall_score: number
  risk_tier: string
  generated_at: string
}

export default function RiskRegisterPage() {
  const [vendors, setVendors] = useState<VendorRisk[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<{ data: { total: number; items: any[] } }>('/vendors?page=1&size=100')
      .then(async res => {
        const risks = []
        for (const v of res.data.items) {
          try {
            const r = await api.get<{ data: VendorRisk }>(`/risk/vendors/${v.vendor_id}`)
            risks.push({ ...r.data, vendor_name: v.vendor_name })
          } catch { /* no risk yet */ }
        }
        risks.sort((a, b) => b.overall_score - a.overall_score)
        setVendors(risks)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Shield className="w-6 h-6 text-sentinel-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Register</h1>
          <p className="text-gray-500 mt-1">Vendors ranked by risk score</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Rank</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Vendor</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Score</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Tier</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={4} className="px-4 py-12 text-center text-gray-500">Loading...</td></tr>
            ) : vendors.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-12 text-center text-gray-500">No risk scores calculated yet. Run import first.</td></tr>
            ) : vendors.map((v, i) => (
              <tr key={v.vendor_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-400 font-mono text-sm">{i + 1}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{v.vendor_name}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`text-lg font-bold ${riskTextColor(v.risk_tier)}`}>
                    {v.overall_score}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`inline-flex items-center gap-1.5 ${riskTextColor(v.risk_tier)} font-medium`}>
                    <span className={`w-2 h-2 rounded-full ${riskColor(v.risk_tier)}`} />
                    {v.risk_tier}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { riskTextColor, riskColor } from '@/lib/utils'
import { Search, Plus, Upload } from 'lucide-react'

interface Vendor {
  vendor_id: string
  vendor_name: string
  vendor_type: string | null
  risk_tier: string | null
  contract_status: string | null
  criticality: string | null
  updated_at: string
}

export default function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [tierFilter, setTierFilter] = useState('')
  const [page, setPage] = useState(1)

  useEffect(() => {
    const params = new URLSearchParams({ page: String(page), size: '20' })
    if (search) params.set('search', search)
    if (tierFilter) params.set('risk_tier', tierFilter)

    api.get<{ data: { total: number; items: Vendor[] } }>(`/vendors?${params}`)
      .then(res => {
        setVendors(res.data.items)
        setTotal(res.data.total)
      })
      .finally(() => setLoading(false))
  }, [page, search, tierFilter])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vendor Registry</h1>
          <p className="text-gray-500 mt-1">{total} vendors</p>
        </div>
        <div className="flex gap-2">
          <a href="/vendors/new" className="flex items-center gap-2 px-4 py-2 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 text-sm font-medium">
            <Plus className="w-4 h-4" /> Add Vendor
          </a>
          <a href="/import" className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium">
            <Upload className="w-4 h-4" /> Import CSV
          </a>
        </div>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search vendors..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500"
          />
        </div>
        <select
          value={tierFilter}
          onChange={e => { setTierFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500"
        >
          <option value="">All Tiers</option>
          <option value="RED">Red</option>
          <option value="YELLOW">Yellow</option>
          <option value="GREEN">Green</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Vendor</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Type</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Risk Tier</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Criticality</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Contract</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">Loading...</td></tr>
            ) : vendors.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">No vendors found</td></tr>
            ) : vendors.map(v => (
              <tr key={v.vendor_id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                onClick={() => window.location.href = `/vendors/${v.vendor_id}`}>
                <td className="px-4 py-3 font-medium text-gray-900">{v.vendor_name}</td>
                <td className="px-4 py-3 text-gray-600">{v.vendor_type || '-'}</td>
                <td className="px-4 py-3">
                  {v.risk_tier && (
                    <span className={`inline-flex items-center gap-1.5 ${riskTextColor(v.risk_tier)} font-medium`}>
                      <span className={`w-2 h-2 rounded-full ${riskColor(v.risk_tier)}`} />
                      {v.risk_tier}
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    v.criticality === 'HIGH' ? 'bg-red-50 text-risk-red' :
                    v.criticality === 'MEDIUM' ? 'bg-yellow-50 text-risk-yellow' :
                    'bg-gray-50 text-gray-600'
                  }`}>{v.criticality || '-'}</span>
                </td>
                <td className="px-4 py-3 text-gray-600">{v.contract_status || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

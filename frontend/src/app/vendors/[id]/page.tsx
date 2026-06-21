'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { api } from '@/lib/api-client'
import { riskTextColor, riskColor } from '@/lib/utils'
import { Building2, Shield, ArrowLeft } from 'lucide-react'

interface VendorDetail {
  vendor_id: string
  vendor_name: string
  vendor_type: string | null
  risk_tier: string | null
  contract_status: string | null
  criticality: string | null
  description: string | null
  updated_at: string
  data_access: { data_type: string; has_access: boolean }[]
}

export default function VendorDetailPage() {
  const params = useParams()
  const [vendor, setVendor] = useState<VendorDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!params.id) return
    api.get<{ data: VendorDetail }>(`/vendors/${params.id}`)
      .then(res => setVendor(res.data))
      .finally(() => setLoading(false))
  }, [params.id])

  if (loading) return <div className="animate-pulse space-y-4"><div className="h-8 w-64 bg-gray-200 rounded" /></div>
  if (!vendor) return <div className="text-gray-500">Vendor not found</div>

  return (
    <div className="space-y-6">
      <a href="/vendors" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="w-4 h-4" /> Back to Vendors
      </a>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-sentinel-50"><Building2 className="w-6 h-6 text-sentinel-600" /></div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{vendor.vendor_name}</h1>
            <p className="text-gray-500">ID: {vendor.vendor_id}</p>
          </div>
          {vendor.risk_tier && (
            <div className="ml-auto flex items-center gap-2">
              <Shield className={`w-5 h-5 ${riskTextColor(vendor.risk_tier)}`} />
              <span className={`text-lg font-bold ${riskTextColor(vendor.risk_tier)}`}>{vendor.risk_tier}</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Details</h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between"><dt className="text-gray-500">Type</dt><dd className="font-medium">{vendor.vendor_type || '-'}</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Criticality</dt><dd className="font-medium">{vendor.criticality || '-'}</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Contract</dt><dd className="font-medium">{vendor.contract_status || '-'}</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Updated</dt><dd className="font-medium">{new Date(vendor.updated_at).toLocaleDateString()}</dd></div>
            </dl>
          </div>
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Data Access</h3>
            {vendor.data_access?.length > 0 ? (
              <ul className="space-y-1 text-sm">
                {vendor.data_access.map((d, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${d.has_access ? 'bg-risk-green' : 'bg-gray-300'}`} />
                    {d.data_type}
                  </li>
                ))}
              </ul>
            ) : <p className="text-sm text-gray-400">No data access records</p>}
          </div>
        </div>
      </div>
    </div>
  )
}

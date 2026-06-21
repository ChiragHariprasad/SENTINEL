'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { FileText, Search } from 'lucide-react'

interface Certification {
  cert_id: string
  vendor_id: string
  framework: string
  status: string
  expires_at: string
  vendor_name?: string
}

export default function CertificationsPage() {
  const [certs, setCerts] = useState<Certification[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.get<{ data: { total: number; items: Certification[] } }>('/certifications')
      .then(res => setCerts(res.data.items))
      .finally(() => setLoading(false))
  }, [])

  const filtered = certs.filter(c =>
    !search || c.framework.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <FileText className="w-6 h-6 text-sentinel-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Certifications</h1>
          <p className="text-gray-500 mt-1">Vendor compliance certifications</p>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input type="text" placeholder="Search frameworks..."
          value={search} onChange={e => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500"
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Framework</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Expires</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={3} className="px-4 py-12 text-center text-gray-500">Loading...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={3} className="px-4 py-12 text-center text-gray-500">No certifications found</td></tr>
            ) : filtered.map(c => (
              <tr key={c.cert_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{c.framework}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    c.status === 'ACTIVE' ? 'bg-green-50 text-risk-green' :
                    c.status === 'EXPIRING' ? 'bg-yellow-50 text-risk-yellow' :
                    'bg-red-50 text-risk-red'
                  }`}>{c.status}</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-500 text-sm">{new Date(c.expires_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

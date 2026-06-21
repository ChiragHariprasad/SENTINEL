'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { ClipboardList, Download, FileText } from 'lucide-react'

interface Report {
  report_id: string
  title: string
  report_type: string
  status: string
  created_at: string
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<{ data: { total: number; items: Report[] } }>('/reports')
      .then(res => setReports(res.data.items))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <ClipboardList className="w-6 h-6 text-sentinel-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-500 mt-1">Generated reports and exports</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Title</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Type</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Created</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Download</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">Loading...</td></tr>
            ) : reports.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">No reports generated yet</td></tr>
            ) : reports.map(r => (
              <tr key={r.report_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{r.title}</td>
                <td className="px-4 py-3 text-gray-600">{r.report_type}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    r.status === 'COMPLETED' ? 'bg-green-50 text-risk-green' : 'bg-yellow-50 text-risk-yellow'
                  }`}>{r.status}</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-500 text-sm">{new Date(r.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3 text-right">
                  <a href={`/api/v1/reports/${r.report_id}/download`}
                    className="text-sentinel-600 hover:text-sentinel-800 inline-flex items-center gap-1 text-sm font-medium">
                    <Download className="w-4 h-4" /> PDF
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

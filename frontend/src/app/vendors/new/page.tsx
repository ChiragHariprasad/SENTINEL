'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api-client'
import { ArrowLeft } from 'lucide-react'

export default function NewVendorPage() {
  const router = useRouter()
  const [form, setForm] = useState({ vendor_name: '', vendor_type: '', criticality: '', contract_status: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const body: Record<string, string> = { vendor_name: form.vendor_name }
      if (form.vendor_type) body.vendor_type = form.vendor_type
      if (form.criticality) body.criticality = form.criticality
      if (form.contract_status) body.contract_status = form.contract_status
      const res = await api.post<{ data: { vendor_id: string } }>('/vendors', body)
      router.push(`/vendors/${res.data.vendor_id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to create vendor')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <a href="/vendors" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="w-4 h-4" /> Back to Vendors
      </a>
      <h1 className="text-2xl font-bold text-gray-900">Add Vendor</h1>
      {error && <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Vendor Name *</label>
          <input type="text" required value={form.vendor_name}
            onChange={e => setForm({ ...form, vendor_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <input type="text" value={form.vendor_type}
            onChange={e => setForm({ ...form, vendor_type: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Criticality</label>
          <select value={form.criticality}
            onChange={e => setForm({ ...form, criticality: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500">
            <option value="">Select...</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Contract Status</label>
          <select value={form.contract_status}
            onChange={e => setForm({ ...form, contract_status: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500">
            <option value="">Select...</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="pending">Pending</option>
          </select>
        </div>
        <button type="submit" disabled={saving}
          className="w-full py-2 px-4 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 disabled:opacity-50 font-medium">
          {saving ? 'Saving...' : 'Create Vendor'}
        </button>
      </form>
    </div>
  )
}

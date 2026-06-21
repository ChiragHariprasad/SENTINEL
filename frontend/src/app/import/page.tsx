'use client'

import { useState } from 'react'
import { api } from '@/lib/api-client'
import { Upload, Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const handleImport = async () => {
    if (!file) return
    setImporting(true)
    setError('')
    setResult(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post<{ data: any }>('/vendors/import', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(res.data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Import failed')
    }
    setImporting(false)
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-2">
        <Upload className="w-6 h-6 text-sentinel-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Import Vendors</h1>
          <p className="text-gray-500 mt-1">Upload vendor_registry.csv to populate the database</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-sentinel-500 transition-colors">
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-500 mb-1">Drop CSV file here or click to browse</p>
            <p className="text-xs text-gray-400">Expected format: vendor_registry.csv</p>
            <input type="file" accept=".csv"
              onChange={e => setFile(e.target.files?.[0] || null)}
              className="mt-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-sentinel-50 file:text-sentinel-700 hover:file:bg-sentinel-100" />
          </div>

          {file && (
            <div className="text-sm text-gray-600">Selected: <span className="font-medium">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)</div>
          )}

          {error && (
            <div className="flex items-center gap-2 text-sm text-risk-red bg-red-50 p-3 rounded-lg">
              <XCircle className="w-4 h-4" /> {error}
            </div>
          )}

          {result && (
            <div className="flex items-center gap-2 text-sm text-risk-green bg-green-50 p-3 rounded-lg">
              <CheckCircle className="w-4 h-4" /> Imported {result.imported || 0} vendors
            </div>
          )}

          <button onClick={handleImport} disabled={!file || importing}
            className="flex items-center gap-2 px-6 py-2 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 text-sm font-medium disabled:opacity-50">
            {importing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            {importing ? 'Importing...' : 'Import CSV'}
          </button>
        </div>
      </div>
    </div>
  )
}

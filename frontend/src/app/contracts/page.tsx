'use client'

import { useState } from 'react'
import { api } from '@/lib/api-client'
import { FileText, Upload, Loader2 } from 'lucide-react'

export default function ContractsPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [contractId, setContractId] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [error, setError] = useState('')

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post<{ data: { contract_id: string } }>('/contracts/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setContractId(res.data.contract_id)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Upload failed')
    }
    setUploading(false)
  }

  const handleAnalyze = async () => {
    if (!contractId) return
    setUploading(true)
    try {
      const res = await api.post(`/contracts/${contractId}/analyze`)
      setAnalysis(res.data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Analysis failed')
    }
    setUploading(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <FileText className="w-6 h-6 text-sentinel-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contracts</h1>
          <p className="text-gray-500 mt-1">Upload and analyze vendor contracts</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 max-w-xl">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Upload Contract</h3>
        <div className="space-y-4">
          <input type="file" accept=".pdf" onChange={e => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-sentinel-50 file:text-sentinel-700 hover:file:bg-sentinel-100" />
          {error && <p className="text-sm text-risk-red">{error}</p>}
          <button onClick={handleUpload} disabled={!file || uploading}
            className="flex items-center gap-2 px-4 py-2 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 text-sm font-medium disabled:opacity-50">
            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            Upload
          </button>
          {contractId && !analysis && (
            <button onClick={handleAnalyze} disabled={uploading}
              className="flex items-center gap-2 px-4 py-2 border border-sentinel-600 text-sentinel-600 rounded-lg hover:bg-sentinel-50 text-sm font-medium">
              Analyze with AI
            </button>
          )}
        </div>
      </div>

      {analysis && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Analysis Results</h3>
          <pre className="text-sm text-gray-600 whitespace-pre-wrap">{JSON.stringify(analysis, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

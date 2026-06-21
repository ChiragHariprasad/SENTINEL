'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'

export default function LoginPage() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      <div className="flex-1 flex flex-col justify-center px-8 lg:px-16 bg-sentinel-900 text-white">
        <h1 className="text-4xl font-bold mb-4">SENTINEL</h1>
        <p className="text-lg text-sentinel-200 mb-2">Third-Party Risk Intelligence Platform</p>
        <p className="text-sm text-sentinel-300">AI-powered vendor risk assessment, monitoring, and compliance tracking.</p>
      </div>
      <div className="flex-1 flex items-center justify-center px-8">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-semibold mb-6 text-gray-900">Sign in</h2>
          {error && <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500"
                placeholder="admin@sentinel.ai"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500"
                placeholder="admin123"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 px-4 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 disabled:opacity-50 font-medium"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import { Users, Shield } from 'lucide-react'

interface User {
  user_id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<{ data: { total: number; items: User[] } }>('/users')
      .then(res => setUsers(res.data.items))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Users className="w-6 h-6 text-sentinel-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-500 mt-1">Administer platform users and roles</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Name</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Email</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Role</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Active</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">Loading...</td></tr>
            ) : users.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-12 text-center text-gray-500">No users found</td></tr>
            ) : users.map(u => (
              <tr key={u.user_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{u.full_name}</td>
                <td className="px-4 py-3 text-gray-600">{u.email}</td>
                <td className="px-4 py-3 text-center">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-sentinel-50 text-sentinel-700">
                    <Shield className="w-3 h-3" /> {u.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`w-2 h-2 rounded-full inline-block ${u.is_active ? 'bg-risk-green' : 'bg-gray-300'}`} />
                </td>
                <td className="px-4 py-3 text-right text-gray-500 text-sm">{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

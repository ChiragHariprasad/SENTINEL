'use client'

import { AuthProvider, useAuth } from '@/lib/auth-context'
import Sidebar from './Sidebar'
import { ReactNode } from 'react'

function AuthGuard({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sentinel-600" />
      </div>
    )
  }

  if (!user) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    return null
  }

  return <>{children}</>
}

export default function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <AuthGuard>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 bg-gray-50 p-8 overflow-auto">
            {children}
          </main>
        </div>
      </AuthGuard>
    </AuthProvider>
  )
}

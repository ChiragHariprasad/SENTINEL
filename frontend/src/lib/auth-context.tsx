'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { api } from './api-client'

interface User {
  email: string
  role: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        setUser({ email: payload.sub || '', role: payload.role || 'analyst' })
      } catch {
        localStorage.clear()
      }
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const res = await api.post<{ data: { access_token: string; refresh_token: string; role: string } }>(
      '/auth/login', { email, password }
    )
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    const payload = JSON.parse(atob(res.data.access_token.split('.')[1]))
    setUser({ email, role: res.data.role })
    router.push('/dashboard')
  }

  const logout = () => {
    localStorage.clear()
    setUser(null)
    router.push('/login')
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

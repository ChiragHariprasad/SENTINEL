const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface FetchOptions extends RequestInit {
  skipAuth?: boolean
}

async function request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { skipAuth, ...fetchOptions } = options

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  }

  if (!skipAuth && typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_URL}/api/v1${endpoint}`, {
    ...fetchOptions,
    headers,
  })

  if (response.status === 401 && !skipAuth) {
    const refresh = localStorage.getItem('refresh_token')
    if (refresh) {
      const refreshRes = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      })
      if (refreshRes.ok) {
        const data = await refreshRes.json()
        localStorage.setItem('access_token', data.data.access_token)
        localStorage.setItem('refresh_token', data.data.refresh_token)
        headers['Authorization'] = `Bearer ${data.data.access_token}`
        const retry = await fetch(`${API_URL}/api/v1${endpoint}`, { ...fetchOptions, headers })
        return retry.json()
      }
      localStorage.clear()
      if (typeof window !== 'undefined') window.location.href = '/login'
    }
  }

  const data = await response.json()
  if (!response.ok) throw new Error(data.error?.message || 'Request failed')
  return data
}

export const api = {
  get: <T>(url: string) => request<T>(url),
  post: <T>(url: string, body?: unknown) => request<T>(url, { method: 'POST', body: JSON.stringify(body) }),
  put: <T>(url: string, body?: unknown) => request<T>(url, { method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(url: string, body?: unknown) => request<T>(url, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(url: string) => request<T>(url, { method: 'DELETE' }),
  upload: <T>(url: string, formData: FormData) => {
    const token = localStorage.getItem('access_token')
    return fetch(`${API_URL}/api/v1${url}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    }).then(r => r.json())
  },
}

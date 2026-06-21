import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/lib/auth-context'

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}))

function TestComponent() {
  const { user, loading } = useAuth()
  if (loading) return <div data-testid="loading">Loading...</div>
  if (user) return <div data-testid="user">{user.email}</div>
  return <div data-testid="no-user">Not logged in</div>
}

describe('AuthProvider', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('shows no user when no token in storage', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    await waitFor(() => {
      expect(screen.getByTestId('no-user')).toBeInTheDocument()
    })
  })

  it('shows user when valid token in storage', async () => {
    const fakeToken =
      'header.' + btoa(JSON.stringify({ sub: 'test@test.com', role: 'analyst' })) + '.signature'
    localStorage.setItem('access_token', fakeToken)

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    await waitFor(() => {
      expect(screen.getByTestId('user')).toBeInTheDocument()
    })
    expect(screen.getByTestId('user').textContent).toBe('test@test.com')
  })
})

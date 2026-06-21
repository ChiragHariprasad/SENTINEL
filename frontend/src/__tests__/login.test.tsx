import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import LoginPage from '@/app/login/page'

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}))

describe('LoginPage', () => {
  it('renders login form with sign in heading', () => {
    render(<LoginPage />)
    expect(screen.getByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
  })

  it('renders email and password fields', () => {
    render(<LoginPage />)
    const emailInput = screen.getByPlaceholderText('admin@sentinel.ai')
    const passwordInput = screen.getByPlaceholderText('admin123')
    expect(emailInput).toBeInTheDocument()
    expect(passwordInput).toBeInTheDocument()
  })

  it('renders sign in button', () => {
    render(<LoginPage />)
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })
})

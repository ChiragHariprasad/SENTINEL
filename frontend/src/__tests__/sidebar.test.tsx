import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Sidebar from '@/components/layout/Sidebar'

jest.mock('next/navigation', () => ({
  usePathname: () => '/dashboard',
}))

describe('Sidebar', () => {
  it('renders brand name', () => {
    render(<Sidebar />)
    expect(screen.getByText('SENTINEL')).toBeInTheDocument()
  })

  it('renders all navigation items', () => {
    render(<Sidebar />)
    const navItems = [
      'Dashboard', 'Vendors', 'Risk Register', 'Anomalies',
      'Evaluation', 'Certifications', 'Alerts', 'Contracts',
      'AI Copilot', 'Reports', 'Admin',
    ]
    for (const item of navItems) {
      expect(screen.getByText(item)).toBeInTheDocument()
    }
  })
})

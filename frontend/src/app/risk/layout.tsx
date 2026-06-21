import DashboardShell from '@/components/layout/Shell'
import { ReactNode } from 'react'

export default function Layout({ children }: { children: ReactNode }) {
  return <DashboardShell>{children}</DashboardShell>
}

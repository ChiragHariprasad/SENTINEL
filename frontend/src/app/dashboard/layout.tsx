import { ReactNode } from 'react'
import DashboardShell from '@/components/layout/Shell'

export default function Layout({ children }: { children: ReactNode }) {
  return <DashboardShell>{children}</DashboardShell>
}

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard, Building2, ShieldAlert, AlertTriangle,
  FileCheck, Bell, FileText, Bot, ClipboardList, Users,
} from 'lucide-react'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/vendors', label: 'Vendors', icon: Building2 },
  { href: '/risk', label: 'Risk Register', icon: ShieldAlert },
  { href: '/anomalies', label: 'Anomalies', icon: AlertTriangle },
  { href: '/evaluation', label: 'Evaluation', icon: FileCheck },
  { href: '/certifications', label: 'Certifications', icon: FileText },
  { href: '/alerts', label: 'Alerts', icon: Bell },
  { href: '/contracts', label: 'Contracts', icon: FileText },
  { href: '/copilot', label: 'AI Copilot', icon: Bot },
  { href: '/reports', label: 'Reports', icon: ClipboardList },
  { href: '/admin/users', label: 'Admin', icon: Users },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-sentinel-900">SENTINEL</h1>
        <p className="text-xs text-gray-500 mt-1">Third-Party Risk Intelligence</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(item => {
          const Icon = item.icon
          const active = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                active
                  ? 'bg-sentinel-50 text-sentinel-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}

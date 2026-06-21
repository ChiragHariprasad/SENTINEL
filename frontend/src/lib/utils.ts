import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function riskColor(tier: string | null | undefined): string {
  switch (tier?.toUpperCase()) {
    case 'RED': return 'bg-risk-red'
    case 'YELLOW': return 'bg-risk-yellow'
    case 'GREEN': return 'bg-risk-green'
    default: return 'bg-gray-400'
  }
}

export function riskTextColor(tier: string | null | undefined): string {
  switch (tier?.toUpperCase()) {
    case 'RED': return 'text-risk-red'
    case 'YELLOW': return 'text-risk-yellow'
    case 'GREEN': return 'text-risk-green'
    default: return 'text-gray-400'
  }
}

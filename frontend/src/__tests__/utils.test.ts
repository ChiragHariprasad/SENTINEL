import { cn, riskTextColor, riskColor } from '@/lib/utils'

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('a', 'b')).toBe('a b')
  })

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', 'visible')).toBe('base visible')
  })
})

describe('riskTextColor', () => {
  it('returns red for RED tier', () => {
    expect(riskTextColor('RED')).toBe('text-risk-red')
  })

  it('returns yellow for YELLOW tier', () => {
    expect(riskTextColor('YELLOW')).toBe('text-risk-yellow')
  })

  it('returns green for GREEN tier', () => {
    expect(riskTextColor('GREEN')).toBe('text-risk-green')
  })

  it('returns default for unknown tier', () => {
    expect(riskTextColor('UNKNOWN')).toBe('text-gray-400')
  })

  it('is case-insensitive', () => {
    expect(riskTextColor('red')).toBe('text-risk-red')
  })
})

describe('riskColor', () => {
  it('returns red bg for RED', () => {
    expect(riskColor('RED')).toBe('bg-risk-red')
  })

  it('returns green bg for GREEN', () => {
    expect(riskColor('GREEN')).toBe('bg-risk-green')
  })

  it('returns gray for unknown', () => {
    expect(riskColor('UNKNOWN')).toBe('bg-gray-400')
  })
})

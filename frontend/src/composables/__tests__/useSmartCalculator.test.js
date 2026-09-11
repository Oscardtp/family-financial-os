import { describe, it, expect } from 'vitest'
import { useSmartCalculator } from '@/composables/useSmartCalculator'

describe('useSmartCalculator.calculateDate', () => {
  const { calculateDate } = useSmartCalculator()

  it('returns null when remaining is Infinity', () => {
    expect(calculateDate(Infinity, 100000)).toBeNull()
  })

  it('returns null when monthly is Infinity', () => {
    expect(calculateDate(5000000, Infinity)).toBeNull()
  })

  it('returns null when remaining is -Infinity', () => {
    expect(calculateDate(-Infinity, 100000)).toBeNull()
  })

  it('returns null when monthly is NaN', () => {
    expect(calculateDate(5000000, NaN)).toBeNull()
  })

  it('returns null when months overflow Date range', () => {
    expect(calculateDate(1e18, 1)).toBeNull()
  })

  it('returns ISO date string for valid inputs', () => {
    const result = calculateDate(5000000, 200000)
    expect(result).toMatch(/\d{4}-\d{2}-\d{2}/)
  })
})

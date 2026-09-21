import { describe, it, expect } from 'vitest'
import { getLocalDateString, parseLocalDate, daysUntil } from '@/composables/useDateFormat'

describe('useDateFormat', () => {
  describe('getLocalDateString', () => {
    it('returns YYYY-MM-DD for a known local date', () => {
      const d = new Date(2026, 8, 20) // Sep 20, 2026 (month is 0-indexed)
      expect(getLocalDateString(d)).toBe('2026-09-20')
    })

    it('returns correct date regardless of hour', () => {
      // Simulate 7 PM Colombia (19:00 local)
      const d = new Date(2026, 8, 20, 19, 0, 0)
      expect(getLocalDateString(d)).toBe('2026-09-20')
    })

    it('returns correct date at 11 PM', () => {
      const d = new Date(2026, 8, 20, 23, 0, 0)
      expect(getLocalDateString(d)).toBe('2026-09-20')
    })

    it('returns correct date at midnight', () => {
      const d = new Date(2026, 8, 21, 0, 0, 0)
      expect(getLocalDateString(d)).toBe('2026-09-21')
    })

    it('returns correct date at 1 AM', () => {
      const d = new Date(2026, 8, 20, 1, 0, 0)
      expect(getLocalDateString(d)).toBe('2026-09-20')
    })

    it('defaults to current date', () => {
      const result = getLocalDateString()
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
      const now = new Date()
      expect(result).toBe(
        `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
      )
    })
  })

  describe('parseLocalDate', () => {
    it('parses YYYY-MM-DD to local Date at midnight', () => {
      const d = parseLocalDate('2026-09-20')
      expect(d.getFullYear()).toBe(2026)
      expect(d.getMonth()).toBe(8) // Sep = 8
      expect(d.getDate()).toBe(20)
      expect(d.getHours()).toBe(0)
      expect(d.getMinutes()).toBe(0)
    })

    it('roundtrips with getLocalDateString', () => {
      const original = '2026-09-20'
      const parsed = parseLocalDate(original)
      const result = getLocalDateString(parsed)
      expect(result).toBe(original)
    })
  })

  describe('daysUntil', () => {
    it('returns 0 for today', () => {
      const today = getLocalDateString()
      expect(daysUntil(today)).toBe(0)
    })

    it('returns positive for future dates', () => {
      const future = new Date()
      future.setDate(future.getDate() + 5)
      expect(daysUntil(getLocalDateString(future))).toBe(5)
    })

    it('returns negative for past dates', () => {
      const past = new Date()
      past.setDate(past.getDate() - 3)
      expect(daysUntil(getLocalDateString(past))).toBe(-3)
    })
  })

  describe('timezone safety', () => {
    it('Colombia 7PM does not shift date', () => {
      // In Colombia (UTC-5), 7PM local = midnight UTC next day
      // toISOString would give wrong date, getLocalDateString should not
      const colombiaEvening = new Date(2026, 8, 20, 19, 0, 0)
      const result = getLocalDateString(colombiaEvening)
      expect(result).toBe('2026-09-20')
      // Prove toISOString would give different result
      const utcResult = colombiaEvening.toISOString().slice(0, 10)
      // In UTC-5, 7PM Sep 20 = midnight Sep 21 UTC
      expect(utcResult).toBe('2026-09-21')
    })

    it('Colombia 11PM does not shift date', () => {
      const colombiaNight = new Date(2026, 8, 20, 23, 0, 0)
      const result = getLocalDateString(colombiaNight)
      expect(result).toBe('2026-09-20')
    })

    it('Colombia midnight crosses to next day correctly', () => {
      const midnight = new Date(2026, 8, 21, 0, 0, 0)
      const result = getLocalDateString(midnight)
      expect(result).toBe('2026-09-21')
    })
  })
})

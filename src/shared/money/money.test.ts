import { describe, it, expect } from 'vitest'
import { Money, CurrencyMismatchError } from '@/shared/money/money'
import type { DineroCurrency } from 'dinero.js'

const EUR: DineroCurrency<bigint> = { code: 'EUR', base: 10n, exponent: 2n }

describe('Money (bigint — no float, ever)', () => {
  it('adds in minor units without floating-point loss', () => {
    // $0.10 + $0.20 = $0.30 (not 0.30000004…)
    const total = Money.USD(10n).add(Money.USD(20n))
    expect(total.amount).toBe(30n)
    expect(total.toDecimal()).toBe('0.30')
  })

  it('subtracts and can go negative', () => {
    const d = Money.USD(250n).subtract(Money.USD(300n))
    expect(d.amount).toBe(-50n)
    expect(d.isNegative()).toBe(true)
    expect(d.isZero()).toBe(false)
  })

  it('negates and zero-checks', () => {
    expect(Money.USD(100n).negate().amount).toBe(-100n)
    expect(Money.USD(0n).isZero()).toBe(true)
    expect(Money.USD(5n).isPositive()).toBe(true)
  })

  it('throws CurrencyMismatchError on cross-currency operations', () => {
    const eur = Money.of(100n, EUR)
    expect(() => Money.USD(100n).add(eur)).toThrow(CurrencyMismatchError)
    expect(() => Money.USD(100n).subtract(eur)).toThrow(CurrencyMismatchError)
    expect(() => Money.USD(100n).equals(eur)).toThrow(CurrencyMismatchError)
    expect(() => Money.USD(100n).compareTo(eur)).toThrow(CurrencyMismatchError)
  })

  it('compares by amount (same currency required)', () => {
    expect(Money.USD(100n).compareTo(Money.USD(50n))).toBe(1)
    expect(Money.USD(50n).compareTo(Money.USD(100n))).toBe(-1)
    expect(Money.USD(100n).compareTo(Money.USD(100n))).toBe(0)
    expect(Money.USD(100n).greaterThan(Money.USD(50n))).toBe(true)
    expect(Money.USD(50n).lessThan(Money.USD(100n))).toBe(true)
  })

  it('formats toDecimal with correct scale', () => {
    expect(Money.USD(250n).toDecimal()).toBe('2.50')
    expect(Money.USD(5n).toDecimal()).toBe('0.05')
    expect(Money.USD(0n).toDecimal()).toBe('0.00')
    expect(Money.USD(123456n).toDecimal()).toBe('1234.56')
  })

  it('is immutable (operations return new instances)', () => {
    const a = Money.USD(100n)
    const b = a.add(Money.USD(50n))
    expect(a.amount).toBe(100n)
    expect(b.amount).toBe(150n)
  })
})

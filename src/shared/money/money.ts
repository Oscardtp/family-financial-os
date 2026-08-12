/**
 * Money value object — Financial Engine foundation.
 *
 * Design (see ADR-004, architecture-rules R6, domain-rules):
 * - Amounts live in MENORES unidades (céntimos) como `bigint`. Nunca `number`/`float`.
 * - Dinero.js v2 `bigint` subpath delegates all math to a bigint calculator (no precision loss).
 * - Currency match is enforced on every operation (`CurrencyMismatchError`).
 * - Immutable: every operation returns a new `Money`.
 *
 * Dinero v2 note (verified via type defs + runtime probe): the `Dinero` object is opaque —
 * its `amount`/`currency`/`scale` are NOT public properties. Read them with `toSnapshot()`.
 */
import {
  dinero,
  add,
  subtract,
  equal,
  compare,
  isZero,
  isPositive,
  isNegative,
  toDecimal,
  toSnapshot,
  type Dinero,
} from 'dinero.js/bigint'
import { USD } from 'dinero.js/bigint/currencies'
import type { DineroCurrency } from 'dinero.js'

export { USD }
export type { Dinero, DineroCurrency }

export class CurrencyMismatchError extends Error {
  public readonly currencyA: string
  public readonly currencyB: string

  constructor(a: string, b: string) {
    super(`Currency mismatch: cannot operate "${a}" with "${b}"`)
    this.name = 'CurrencyMismatchError'
    this.currencyA = a
    this.currencyB = b
  }
}

export class Money {
  public readonly amount: bigint
  public readonly currency: string
  public readonly scale: number
  private readonly _d: Dinero<bigint>

  private constructor(d: Dinero<bigint>) {
    this._d = d
    const snap = toSnapshot(d)
    this.amount = snap.amount
    this.currency = snap.currency.code
    this.scale = Number(snap.currency.exponent)
  }

  static of(amount: bigint, currency: DineroCurrency<bigint>): Money {
    if (typeof amount !== 'bigint') {
      throw new TypeError(`Money amount must be a bigint (got ${typeof amount})`)
    }
    return new Money(dinero({ amount, currency }))
  }

  static USD(cents: bigint): Money {
    return Money.of(cents, USD)
  }

  static zero(currency: DineroCurrency<bigint>): Money {
    return Money.of(0n, currency)
  }

  private assertSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new CurrencyMismatchError(this.currency, other.currency)
    }
  }

  add(other: Money): Money {
    this.assertSameCurrency(other)
    return new Money(add(this._d, other._d))
  }

  subtract(other: Money): Money {
    this.assertSameCurrency(other)
    return new Money(subtract(this._d, other._d))
  }

  negate(): Money {
    return new Money(dinero({ amount: -this.amount, currency: toSnapshot(this._d).currency }))
  }

  equals(other: Money): boolean {
    this.assertSameCurrency(other)
    return equal(this._d, other._d)
  }

  compareTo(other: Money): number {
    this.assertSameCurrency(other)
    return Number(compare(this._d, other._d))
  }

  greaterThan(other: Money): boolean {
    return this.compareTo(other) > 0
  }

  lessThan(other: Money): boolean {
    return this.compareTo(other) < 0
  }

  isZero(): boolean {
    return isZero(this._d)
  }

  isPositive(): boolean {
    return isPositive(this._d)
  }

  isNegative(): boolean {
    return isNegative(this._d)
  }

  toDecimal(): string {
    return toDecimal(this._d)
  }

  toString(): string {
    return `${this.toDecimal()} ${this.currency}`
  }

  toJSON(): { amount: string; currency: string; scale: number } {
    return { amount: this.amount.toString(), currency: this.currency, scale: this.scale }
  }
}

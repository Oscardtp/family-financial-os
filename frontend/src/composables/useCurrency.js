/**
 * Shared currency and date formatting for COP (pesos colombianos).
 *
 * Usage:
 *   import { useCurrency } from '@/composables/useCurrency'
 *   const { fmt, fmtFull } = useCurrency()
 *   <span>${{ fmt(1500000) }}</span>   →  $1.500.000
 *   <span>{{ fmtFull(1500000) }}</span> →  $1.500.000
 */

const formatter = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 0 })
const fullFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

export function useCurrency() {
  /**
   * Formatea un número como COP sin símbolo de moneda.
   * fmt(1500000) → "1.500.000"
   */
  function fmt(value, decimals = 0) {
    const n = Number(value || 0)
    if (decimals === 0) return formatter.format(n)
    return new Intl.NumberFormat('es-CO', { maximumFractionDigits: decimals }).format(n)
  }

  /**
   * Formatea un número como COP con símbolo $.
   * fmtFull(1500000) → "$1.500.000"
   */
  function fmtFull(value) {
    const n = Number(value || 0)
    return '$' + formatter.format(n)
  }

  /**
   * Formatea una fecha ISO a formato legible.
   * fmtDate('2025-03-15') → "15 mar. 2025"
   */
  function fmtDate(dateStr) {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return '-'
    return d.toLocaleDateString('es-CO', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  }

  /**
   * Formatea una fecha ISO solo mes y año.
   * fmtMonth('2025-03-15') → "marzo 2025"
   */
  function fmtMonth(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return ''
    return d.toLocaleDateString('es-CO', {
      month: 'long',
      year: 'numeric',
    })
  }

  return { fmt, fmtFull, fmtDate, fmtMonth }
}

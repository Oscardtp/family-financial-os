/**
 * Dynamic "Fecha Objetivo" (target date) estimation for savings goals.
 *
 * Given a target amount and a monthly contribution, it estimates the date
 * on which the goal could be reached and flags an early warning when the
 * horizon exceeds 10 years (120 months).
 *
 * The existing date utilities in `useSmartCalculator` are left untouched;
 * this composable is a focused, pure helper used as a readonly estimator
 * across the goal forms.
 *
 * Usage:
 *   import { useGoalDate } from '@/composables/useGoalDate'
 *   const { calcularFechaObjetivo } = useGoalDate()
 *   const info = calcularFechaObjetivo(5000000, 200000)
 *   // { fechaObjetivo: '...', meses: 25, warning: '' }
 */

const WARNING_MES = 'El monto objetivo puede ser demasiado alto para tu aporte mensual. Con lo que ahorras, te tomaría más de 10 años.'

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : NaN
}

function isValidAmount(value) {
  const n = toNumber(value)
  return Number.isFinite(n) && n > 0
}

export function calcularFechaObjetivo(montoObjetivo, aporteMensual) {
  if (!isValidAmount(montoObjetivo) || !isValidAmount(aporteMensual)) {
    return null
  }

  const monto = toNumber(montoObjetivo)
  const aporte = toNumber(aporteMensual)
  const meses = Math.ceil(monto / aporte)

  const fecha = new Date()
  fecha.setMonth(fecha.getMonth() + meses)
  if (Number.isNaN(fecha.getTime())) return null

  const fechaStr = fecha.toLocaleDateString('es-CO', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  const warning = meses > 120 ? WARNING_MES : ''

  return { fechaObjetivo: fechaStr, meses, warning }
}

export function useGoalDate() {
  return { calcularFechaObjetivo }
}

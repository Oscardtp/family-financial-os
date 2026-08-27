/**
 * Smart field calculation for savings goals.
 * Auto-computes monthly contribution from date, or date from monthly contribution.
 */

import { useCurrency } from '@/composables/useCurrency'

function monthsUntil(targetDate) {
  if (!targetDate) return 0
  const now = new Date()
  const target = new Date(targetDate + 'T00:00:00')
  const months = (target.getFullYear() - now.getFullYear()) * 12 + (target.getMonth() - now.getMonth())
  return Math.max(months, 1)
}

function calculateMonthly(remaining, targetDate) {
  if (!remaining || remaining <= 0 || !targetDate) return 0
  const months = monthsUntil(targetDate)
  return Math.ceil(remaining / months)
}

function calculateDate(remaining, monthly) {
  if (!remaining || remaining <= 0 || !monthly || monthly <= 0) return null
  const months = Math.ceil(remaining / monthly)
  const target = new Date()
  target.setMonth(target.getMonth() + months)
  return target.toISOString().split('T')[0]
}

function formatDateStr(d) {
  if (!d) return ''
  const date = new Date(d + 'T00:00:00')
  return date.toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })
}

export function useSmartCalculator() {
  const { fmt } = useCurrency()

  function calcSmartFields(targetAmount, targetDate, monthlyContribution, currentAmount) {
    const remaining = Math.max((targetAmount || 0) - (currentAmount || 0), 0)
    const result = { monthly: false, date: false, summary: '' }

    if (remaining <= 0) return result

    const hasDate = !!targetDate
    const hasMonthly = monthlyContribution > 0

    if (hasDate && !hasMonthly) {
      const calc = calculateMonthly(remaining, targetDate)
      result.monthly = true
      result.summary = `Necesitas ahorrar $${fmt(calc)} al mes para llegar a tu meta.`
    } else if (hasMonthly && !hasDate) {
      const calc = calculateDate(remaining, monthlyContribution)
      if (calc) {
        result.date = true
        result.summary = `Llegarás a tu meta el ${formatDateStr(calc)} ahorrando $${fmt(monthlyContribution)} al mes.`
      }
    } else if (hasDate && hasMonthly) {
      const months = monthsUntil(targetDate)
      const canSave = monthlyContribution * months
      if (canSave >= remaining) {
        result.summary = `Con $${fmt(monthlyContribution)} al mes durante ${months} meses, ahorrarás $${fmt(canSave)}. Llegarás a tu meta.`
      } else {
        const shortfall = remaining - canSave
        result.summary = `Con $${fmt(monthlyContribution)} al mes durante ${months} meses, ahorrarás $${fmt(canSave)}. Te faltan $${fmt(shortfall)}.`
      }
    }

    return result
  }

  return {
    calcSmartFields,
    monthsUntil,
    calculateMonthly,
    calculateDate,
    formatMoney: fmt,
    formatDate: formatDateStr,
  }
}

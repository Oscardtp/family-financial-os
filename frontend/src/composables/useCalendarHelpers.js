/**
 * Pure helper functions for calendar event display logic.
 * No side effects — fully testable.
 */

function daysUntil(dateStr) {
  if (!dateStr) return null
  const d = new Date(dateStr + 'T00:00:00')
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return Math.round((d - now) / 86400000)
}

export function eventColor(ev) {
  if (ev.status === 'paid') return 'ev-paid'
  if (ev.type === 'income') return 'ev-income'
  if (ev.type === 'debt') return 'ev-debt'
  if (ev.type === 'goal') return 'ev-goal'
  const diff = daysUntil(ev.due_date)
  if (diff === null) return 'ev-default'
  if (diff < 0) return 'ev-overdue'
  if (ev.cutoff_date && daysUntil(ev.cutoff_date) <= 1) return 'ev-overdue'
  if (diff <= (ev.reminder_days_before || 3)) return 'ev-upcoming'
  return 'ev-expense'
}

export function statusLabel(ev) {
  if (ev.status === 'paid') return 'Pagado'
  const diff = daysUntil(ev.due_date)
  if (diff === null) return 'Pendiente'
  if (diff < 0) return 'Atrasado'
  if (diff === 0) return 'Vence hoy'
  if (diff <= (ev.reminder_days_before || 3)) return 'Próximo'
  return 'Pendiente'
}

export function statusClass(ev) {
  if (ev.status === 'paid') return 'st-green'
  const diff = daysUntil(ev.due_date)
  if (diff === null) return 'st-yellow'
  return diff <= 0 ? 'st-red' : 'st-yellow'
}

export function methodLabel(m) {
  return { card: 'Tarjeta', cash: 'Efectivo', transfer: 'Transferencia' }[m] || m
}

export function typeIcon(type, { TrendingUp, Target, CreditCard, Wallet, Bell }) {
  if (type === 'income') return TrendingUp
  if (type === 'goal') return Target
  if (type === 'debt') return CreditCard
  if (type === 'payment') return Wallet
  return Bell
}

export function fmtDateShort(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const diff = Math.round((d - now) / 86400000)
  if (isNaN(diff)) return ''
  if (diff === 0) return 'hoy'
  if (diff === 1) return 'mañana'
  if (diff < 7) return `en ${diff} días`
  return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' })
}

export function isCutoffUrgent(ev) {
  if (!ev.cutoff_date || ev.status === 'paid') return false
  const diff = daysUntil(ev.cutoff_date)
  if (diff === null) return false
  return diff <= 1
}

export function confidenceLabel(ev) {
  if (ev.confidence >= 100) return 'Confirmado'
  if (ev.confidence >= 70) return 'Aprendido'
  return 'Estimado'
}

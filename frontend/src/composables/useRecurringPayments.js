import { ref, computed } from 'vue'

const freqLabels = {
  weekly: 'Semanal',
  biweekly: 'Quincenal',
  monthly: 'Mensual',
  yearly: 'Anual',
}

const freqLabelsFull = {
  weekly: 'Cada semana',
  biweekly: 'Cada 2 semanas',
  monthly: 'Cada mes',
  yearly: 'Cada año',
}

function daysUntil(dateStr) {
  if (!dateStr) return null
  const target = new Date(dateStr + 'T00:00:00')
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return Math.round((target - now) / 86400000)
}

function formatFrequency(frequency, dayOfMonth) {
  if (frequency === 'monthly' && dayOfMonth) {
    return `Cada mes, día ${dayOfMonth}`
  }
  if (frequency === 'weekly') return 'Cada semana'
  if (frequency === 'biweekly') return 'Cada 2 semanas'
  if (frequency === 'yearly') return 'Cada año'
  return freqLabels[frequency] || frequency
}

function formatDueDate(nextDueDate) {
  if (!nextDueDate) return { text: '-', color: 'neutral' }
  const diff = daysUntil(nextDueDate)
  if (diff < 0) return { text: 'Vencido', color: 'error' }
  if (diff === 0) return { text: 'Hoy', color: 'warning' }
  if (diff === 1) return { text: 'Mañana', color: 'warning' }
  if (diff <= 3) return { text: `En ${diff} días`, color: 'warning' }
  if (diff <= 7) return { text: `En ${diff} días`, color: 'neutral' }
  return { text: `En ${diff} días`, color: 'neutral' }
}

function statusLabel(isActive, nextDueDate) {
  if (!isActive) return 'Inactivo'
  const { text, color } = formatDueDate(nextDueDate)
  return `Activo · ${text}`
}

export function useRecurringPayments() {
  const frequencyOptions = [
    { value: 'weekly', label: 'Semanal' },
    { value: 'biweekly', label: 'Quincenal' },
    { value: 'monthly', label: 'Mensual' },
    { value: 'yearly', label: 'Anual' },
  ]

  const typeOptions = [
    { value: 'expense', label: 'Gasto' },
    { value: 'income', label: 'Ingreso' },
  ]

  const days = Array.from({ length: 28 }, (_, i) => i + 1)

  return {
    frequencyOptions,
    typeOptions,
    days,
    formatFrequency,
    formatDueDate,
    statusLabel,
    daysUntil,
    freqLabels,
    freqLabelsFull,
  }
}

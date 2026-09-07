import { useCurrency } from '@/composables/useCurrency'

export function useFinancialHelpers() {
  const { fmt } = useCurrency()

  function calcPercentage(value, total) {
    if (!total || total <= 0) return 0
    return Math.round((value / total) * 100)
  }

  function safeNumber(value, fallback = 0) {
    const num = Number(value)
    return Number.isFinite(num) ? num : fallback
  }

  return {
    fmt,
    calcPercentage,
    safeNumber,
  }
}

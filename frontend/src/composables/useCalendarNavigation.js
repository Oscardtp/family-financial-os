import { computed } from 'vue'
import { useCalendarStore } from '@/stores/useCalendar'

export function useCalendarNavigation() {
  const store = useCalendarStore()

  const monthLabel = computed(() =>
    new Date(store.year, store.month - 1, 1).toLocaleDateString('es-CO', {
      month: 'long',
      year: 'numeric',
    })
  )

  function prevMonth() {
    let m = store.month - 1
    let y = store.year
    if (m < 1) { m = 12; y-- }
    store.fetchRange(y, m)
  }

  function nextMonth() {
    let m = store.month + 1
    let y = store.year
    if (m > 12) { m = 1; y++ }
    store.fetchRange(y, m)
  }

  function goToday() {
    const now = new Date()
    store.fetchRange(now.getFullYear(), now.getMonth() + 1)
  }

  return { store, monthLabel, prevMonth, nextMonth, goToday }
}

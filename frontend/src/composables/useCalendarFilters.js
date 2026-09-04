import { ref, computed } from 'vue'
import { useCalendarStore } from '@/stores/useCalendar'

const WEEKDAYS = ['L', 'M', 'M', 'J', 'V', 'S', 'D']

const FILTERS = [
  { key: 'all', label: 'Todos' },
  { key: 'payments', label: 'Pagos' },
  { key: 'recurring', label: 'Recurrentes' },
  { key: 'income', label: 'Ingresos' },
]

export function useCalendarFilters() {
  const store = useCalendarStore()
  const activeFilter = ref('all')

  function matchesFilter(ev) {
    if (activeFilter.value === 'all') return true
    if (activeFilter.value === 'income') return ev.type === 'income'
    if (activeFilter.value === 'recurring') return ev.is_recurrent === true
    if (activeFilter.value === 'payments') return ev.type !== 'income' && !ev.is_recurrent
    return true
  }

  const calendarDays = computed(() => {
    const now = new Date()
    const y = Number.isFinite(store.year) ? store.year : now.getFullYear()
    const m = Number.isFinite(store.month) ? store.month : now.getMonth() + 1
    const first = new Date(y, m - 1, 1)
    const offset = (first.getDay() + 6) % 7
    const start = new Date(y, m - 1, 1 - offset)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const cells = []
    for (let i = 0; i < 42; i++) {
      const d = new Date(start)
      d.setDate(start.getDate() + i)
      if (isNaN(d.getTime())) continue
      const inMonth = d.getMonth() === m - 1
      cells.push({
        day: d.getDate(),
        dateStr: d.toISOString().slice(0, 10),
        inMonth,
        isToday: d.getTime() === today.getTime(),
        events: [],
      })
    }
    for (const ev of store.events) {
      if (!matchesFilter(ev)) continue
      const cell = cells.find((c) => c.dateStr === ev.due_date)
      if (cell) cell.events.push(ev)
    }
    return cells
  })

  const filteredCalendarDays = computed(() => calendarDays.value)

  const filteredListGrouped = computed(() => {
    const filtered = store.events.filter(ev => matchesFilter(ev))
    const groups = {}
    for (const ev of filtered) {
      if (!groups[ev.due_date]) {
        const d = new Date(ev.due_date + 'T00:00:00')
        groups[ev.due_date] = {
          dateStr: ev.due_date,
          dayNum: d.getDate(),
          dayLabel: d.toLocaleDateString('es-CO', { weekday: 'long', month: 'long', day: 'numeric' }),
          events: [],
        }
      }
      groups[ev.due_date].events.push(ev)
    }
    return Object.values(groups).sort((a, b) => a.dateStr.localeCompare(b.dateStr))
  })

  return {
    store,
    WEEKDAYS,
    FILTERS,
    activeFilter,
    matchesFilter,
    filteredCalendarDays,
    filteredListGrouped,
  }
}

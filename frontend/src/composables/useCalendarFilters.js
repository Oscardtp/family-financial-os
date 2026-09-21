import { ref, computed } from 'vue'
import { useCalendarStore } from '@/stores/useCalendar'
import { getLocalDateString } from '@/composables/useDateFormat'

const WEEKDAYS = ['L', 'M', 'M', 'J', 'V', 'S', 'D']

const FILTERS = [
  { key: 'all', label: 'Todo' },
  { key: 'income', label: 'Ingresos' },
  { key: 'expense', label: 'Gastos' },
  { key: 'debt', label: 'Pagos' },
  { key: 'goal', label: 'Metas' },
]

export function useCalendarFilters() {
  const store = useCalendarStore()
  const activeFilter = ref('all')

  function matchesFilter(ev) {
    if (activeFilter.value === 'all') return true
    return ev.type === activeFilter.value
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
        dateStr: getLocalDateString(d),
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

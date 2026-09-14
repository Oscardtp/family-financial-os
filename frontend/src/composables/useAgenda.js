import { ref } from 'vue'
import { eventsService } from '@/services/events'

export function useAgenda() {
  const upcomingEvents = ref([])
  const availability = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function loadUpcoming(days = 14) {
    loading.value = true
    error.value = null
    try {
      const res = await eventsService.upcoming(days)
      upcomingEvents.value = res.data || []
    } catch {
      upcomingEvents.value = []
      error.value = 'No pudimos cargar los próximos movimientos.'
    } finally {
      loading.value = false
    }
  }

  async function loadAvailability(days = 30) {
    try {
      const res = await eventsService.availability(days)
      availability.value = res.data
    } catch {
      availability.value = null
    }
  }

  function groupByDate(events) {
    const groups = {}
    for (const ev of events) {
      if (!groups[ev.due_date]) {
        groups[ev.due_date] = {
          dateStr: ev.due_date,
          events: [],
        }
      }
      groups[ev.due_date].events.push(ev)
    }
    return Object.values(groups).sort((a, b) => a.dateStr.localeCompare(b.dateStr))
  }

  function formatGroupLabel(dateStr) {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const target = new Date(dateStr + 'T00:00:00')
    const diff = Math.round((target - today) / 86400000)
    if (diff === 0) return 'HOY'
    if (diff === 1) return 'MAÑANA'
    return target.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' }).toUpperCase()
  }

  return {
    upcomingEvents,
    availability,
    loading,
    error,
    loadUpcoming,
    loadAvailability,
    groupByDate,
    formatGroupLabel,
  }
}

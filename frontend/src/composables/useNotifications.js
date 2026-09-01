import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'
import { eventsService, coachService } from '@/services/events'
import { useCurrency } from '@/composables/useCurrency'

export function useNotifications() {
  const notifications = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const upcoming = ref({ today: [], this_week: [] })
  const upcomingLoading = ref(false)
  const upcomingFilter = ref('all')

  const suggestions = ref([])
  const suggestionsLoading = ref(false)

  async function load() {
    loading.value = true
    try {
      const [notifRes, countRes] = await Promise.all([
        api.get('/notifications'),
        api.get('/notifications/unread-count'),
      ])
      notifications.value = notifRes.data
      unreadCount.value = countRes.data.count
    } catch (e) {
      console.error('Error loading notifications:', e)
    } finally {
      loading.value = false
    }
  }

  async function loadUpcoming(days = 7) {
    upcomingLoading.value = true
    try {
      const { data } = await api.get('/notifications/upcoming', { params: { days } })
      upcoming.value = data
    } catch (e) {
      console.error('Error loading upcoming notifications:', e)
    } finally {
      upcomingLoading.value = false
    }
  }

  async function loadSuggestions() {
    suggestionsLoading.value = true
    try {
      const { data } = await coachService.suggestions()
      suggestions.value = data
    } catch (e) {
      console.error('Error loading coach suggestions:', e)
    } finally {
      suggestionsLoading.value = false
    }
  }

  async function acceptSuggestion(suggestion) {
    try {
      await coachService.accept({
        name: suggestion.name,
        type: suggestion.type,
        amount: suggestion.amount,
        anchor_day: suggestion.anchor_day,
        recommended_offset_days: 5,
        generate_months: 12,
        source: 'LEARNED',
      })
      await loadSuggestions()
      await loadUpcoming()
    } catch (e) {
      console.error('Error accepting suggestion:', e)
      throw e
    }
  }

  const filteredUpcoming = () => {
    const { fmt } = useCurrency()
    const groups = upcoming.value
    if (upcomingFilter.value === 'all') {
      return [
        ...groups.today.map(n => ({ ...n, amountFormatted: fmt(n.amount) })),
        ...groups.this_week.map(n => ({ ...n, amountFormatted: fmt(n.amount) })),
      ]
    }
    const map = { today: 'today', esta_semana: 'this_week' }
    const key = map[upcomingFilter.value]
    if (!key) return []
    return groups[key].map(n => ({ ...n, amountFormatted: fmt(n.amount) }))
  }

  async function markPaid(eventId) {
    try {
      await eventsService.pay(eventId)
      await loadUpcoming()
      await load()
    } catch (e) {
      console.error('Error marking as paid:', e)
      throw e
    }
  }

  async function markAllRead() {
    try {
      await api.post('/notifications/read-all')
      notifications.value.forEach(n => (n.is_read = true))
      unreadCount.value = 0
    } catch (e) {
      console.error('Error marking notifications:', e)
    }
  }

  function markRead(notif) {
    if (!notif.is_read) {
      api.post(`/notifications/${notif.id}/read`).catch(() => {})
      notif.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }

  function useClickOutside(bellRef, isOpen) {
    function handleClick(e) {
      if (bellRef.value && !bellRef.value.contains(e.target)) {
        isOpen.value = false
      }
    }
    onMounted(() => document.addEventListener('click', handleClick))
    onUnmounted(() => document.removeEventListener('click', handleClick))
  }

  return {
    notifications,
    unreadCount,
    loading,
    upcoming,
    upcomingLoading,
    upcomingFilter,
    filteredUpcoming,
    suggestions,
    suggestionsLoading,
    load,
    loadUpcoming,
    loadSuggestions,
    acceptSuggestion,
    markPaid,
    markAllRead,
    markRead,
    useClickOutside,
  }
}

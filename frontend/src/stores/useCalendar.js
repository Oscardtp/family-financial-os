import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { eventsService, obligationsService } from '@/services/events'
import { useCurrency } from '@/composables/useCurrency'

export const useCalendarStore = defineStore('calendar', () => {
  const { fmt, fmtFull, fmtDate } = useCurrency()

  const events = ref([])
  const obligations = ref([])
  const loading = ref(false)
  const error = ref(null)
  const year = ref(new Date().getFullYear())
  const month = ref(new Date().getMonth() + 1)

  const selectedEvent = ref(null)
  const detailOpen = ref(false)
  const createOpen = ref(false)

  const availability = ref(null)
  const availabilityDays = ref(7)
  const availabilityLoading = ref(false)

  const accounts = ref([])
  const members = ref([])

  const availabilitySummary = computed(() => {
    const a = availability.value
    if (!a) return null
    return {
      available: fmt(a.available),
      upcoming: fmt(a.upcoming_payments),
      projected: fmt(a.projected_available),
      cashNeeded: fmt(a.cash_needed),
      expectedIncome: fmt(a.expected_income),
      expectedExpenses: fmt(a.expected_expenses),
      budgetCommitted: fmt(a.budget_committed),
    }
  })

  async function fetchRange(y = year.value, m = month.value) {
    year.value = y
    month.value = m
    loading.value = true
    error.value = null
    try {
      const from = new Date(y, m - 2, 1)
      const to = new Date(y, m + 2, 0)
      const res = await eventsService.listRange(
        from.toISOString().slice(0, 10),
        to.toISOString().slice(0, 10)
      )
      events.value = res.data
    } catch {
      error.value = 'No pudimos cargar tu calendario. Revisa tu conexión e intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  async function fetchMonth(y = year.value, m = month.value) {
    return fetchRange(y, m)
  }

  async function fetchObligations() {
    try {
      const res = await obligationsService.list()
      obligations.value = res.data
    } catch {
      obligations.value = []
    }
  }

  async function fetchAvailability(days = 7) {
    availabilityDays.value = days
    availabilityLoading.value = true
    try {
      const res = await eventsService.availability(days)
      availability.value = res.data
    } catch {
      availability.value = null
    } finally {
      availabilityLoading.value = false
    }
  }

  async function fetchAccounts() {
    try {
      const res = await eventsService.accounts()
      accounts.value = res.data
    } catch {
      accounts.value = []
    }
  }

  async function fetchMembers() {
    try {
      const res = await eventsService.household()
      members.value = res.data?.members || []
    } catch {
      members.value = []
    }
  }

  function openEvent(event) {
    selectedEvent.value = event
    detailOpen.value = true
  }

  function closeDetail() {
    detailOpen.value = false
    selectedEvent.value = null
  }

  async function markPaid(event) {
    try {
      const res = await eventsService.pay(event.id)
      const idx = events.value.findIndex((e) => e.id === event.id)
      if (idx !== -1) events.value[idx] = res.data
      if (selectedEvent.value && selectedEvent.value.id === event.id) {
        selectedEvent.value = res.data
      }
      return { error: null }
    } catch {
      return { error: 'No pudimos marcar el pago. Intenta de nuevo.' }
    }
  }

  async function createEvent(data) {
    try {
      await eventsService.create(data)
      await fetchRange()
      createOpen.value = false
      return { error: null }
    } catch {
      return { error: 'No pudimos crear el evento. Revisa los datos e intenta de nuevo.' }
    }
  }

  return {
    events, obligations, loading, error, year, month,
    selectedEvent, detailOpen, createOpen,
    availability, availabilityDays, availabilityLoading, availabilitySummary,
    accounts, members,
    fetchRange, fetchMonth, fetchObligations, fetchAvailability, fetchAccounts, fetchMembers,
    openEvent, closeDetail, markPaid, createEvent,
    fmt, fmtFull, fmtDate,
  }
})

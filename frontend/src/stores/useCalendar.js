import { defineStore } from 'pinia'
import { ref } from 'vue'
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

  const accounts = ref([])
  const members = ref([])

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

  async function unpayEvent(event) {
    try {
      const res = await eventsService.unpay(event.id)
      const idx = events.value.findIndex((e) => e.id === event.id)
      if (idx !== -1) events.value[idx] = res.data
      if (selectedEvent.value && selectedEvent.value.id === event.id) {
        selectedEvent.value = res.data
      }
      return { error: null }
    } catch {
      return { error: 'No pudimos anular el pago. Intenta de nuevo.' }
    }
  }

  async function createEvent(data) {
    try {
      await eventsService.create(data)
      await fetchRange()
      return { error: null }
    } catch {
      return { error: 'No pudimos crear el evento. Revisa los datos e intenta de nuevo.' }
    }
  }

  async function editEvent(eventId, data) {
    try {
      const res = await eventsService.update(eventId, data)
      const idx = events.value.findIndex((e) => e.id === eventId)
      if (idx !== -1) events.value[idx] = res.data
      if (selectedEvent.value && selectedEvent.value.id === eventId) {
        selectedEvent.value = res.data
      }
      return { error: null }
    } catch {
      return { error: 'No pudimos guardar los cambios. Intenta de nuevo.' }
    }
  }

  async function deleteEvent(eventId) {
    try {
      await eventsService.remove(eventId)
      events.value = events.value.filter((e) => e.id !== eventId)
      closeDetail()
      return { error: null }
    } catch {
      return { error: 'No pudimos eliminar el evento. Intenta de nuevo.' }
    }
  }

  async function toggleObligationActive(obligationId) {
    const ob = obligations.value.find(o => o.id === obligationId)
    if (!ob) return { error: 'No encontramos esta obligación.' }
    try {
      const res = await obligationsService.update(obligationId, { is_active: !ob.is_active })
      const idx = obligations.value.findIndex(o => o.id === obligationId)
      if (idx !== -1) obligations.value[idx] = res.data
      return { error: null }
    } catch {
      return { error: 'No pudimos cambiar el estado. Intenta de nuevo.' }
    }
  }

  async function deleteObligation(obligationId) {
    try {
      await obligationsService.remove(obligationId)
      obligations.value = obligations.value.filter(o => o.id !== obligationId)
      return { error: null }
    } catch {
      return { error: 'No pudimos eliminar la obligación. Intenta de nuevo.' }
    }
  }

  async function createObligation(data) {
    try {
      const res = await obligationsService.create(data)
      obligations.value.push(res.data)
      return { error: null }
    } catch {
      return { error: 'No pudimos crear la obligación. Intenta de nuevo.' }
    }
  }

  return {
    events, obligations, loading, error, year, month,
    selectedEvent, detailOpen,
    accounts, members,
    fetchRange, fetchMonth, fetchObligations, fetchAccounts, fetchMembers,
    openEvent, closeDetail, markPaid, unpayEvent, createEvent, editEvent, deleteEvent,
    toggleObligationActive, deleteObligation, createObligation,
    fmt, fmtFull, fmtDate,
  }
})

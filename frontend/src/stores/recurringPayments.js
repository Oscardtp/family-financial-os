import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { useCurrency } from '@/composables/useCurrency'

export const useRecurringPaymentsStore = defineStore('recurringPayments', () => {
  const { fmt, fmtFull, fmtDate } = useCurrency()

  const items = ref([])
  const loading = ref(false)
  const error = ref(null)
  const selectedId = ref(null)
  const history = ref([])

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/recurring-payments')
      items.value = res.data || []
      return { error: null }
    } catch {
      error.value = 'No pudimos cargar los pagos recurrentes.'
      return { error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function pay(id) {
    try {
      const res = await api.post(`/recurring-payments/${id}/pay`)
      const idx = items.value.findIndex((i) => i.id === id)
      if (idx !== -1) items.value[idx] = res.data
      return { error: null }
    } catch {
      return { error: 'No pudimos registrar el pago. Intenta de nuevo.' }
    }
  }

  async function fetchHistory(id) {
    try {
      const res = await api.get(`/recurring-payments/${id}/payments`)
      history.value = res.data || []
      selectedId.value = id
      return { error: null }
    } catch {
      return { error: 'No pudimos cargar el historial.' }
    }
  }

  async function update(id, data) {
    try {
      const res = await api.put(`/recurring-payments/${id}`, data)
      const idx = items.value.findIndex((i) => i.id === id)
      if (idx !== -1) items.value[idx] = res.data
      return { error: null }
    } catch {
      return { error: 'No pudimos guardar los cambios. Intenta de nuevo.' }
    }
  }

  async function create(data) {
    try {
      const res = await api.post('/recurring-payments', data)
      items.value.push(res.data)
      return { error: null }
    } catch {
      return { error: 'No pudimos crear el pago recurrente. Revisa los datos e intenta de nuevo.' }
    }
  }

  async function remove(id) {
    try {
      await api.delete(`/recurring-payments/${id}`)
      items.value = items.value.filter((i) => i.id !== id)
      return { error: null }
    } catch {
      return { error: 'No pudimos eliminar el pago recurrente. Intenta de nuevo.' }
    }
  }

  async function toggleActive(id) {
    const item = items.value.find((i) => i.id === id)
    if (!item) return { error: 'No encontramos este pago recurrente.' }
    return update(id, { is_active: !item.is_active })
  }

  return {
    items, loading, error, selectedId, history,
    fetchAll, pay, fetchHistory, update, create, remove, toggleActive,
    fmt, fmtFull, fmtDate,
  }
})

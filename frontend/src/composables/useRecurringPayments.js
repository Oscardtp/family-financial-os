import { ref } from 'vue'
import api from '@/services/api'

export function useRecurringPayments() {
  const history = ref([])
  const historyLoading = ref(false)
  const historyError = ref(null)
  const executing = ref(false)

  async function getPaymentHistory(paymentId) {
    if (!paymentId) return []
    historyLoading.value = true
    historyError.value = null
    try {
      const { data } = await api.get(`/recurring-payments/${paymentId}/payments`)
      history.value = data
      return data
    } catch (e) {
      historyError.value = e.response?.data?.detail || 'Error al cargar historial'
      history.value = []
      return []
    } finally {
      historyLoading.value = false
    }
  }

  async function getPendingEvent(paymentId) {
    const { data } = await api.get(`/recurring-payments/${paymentId}/pending-event`)
    return data
  }

  async function executeRecurringPayment(eventId) {
    executing.value = true
    try {
      await api.post(`/events/${eventId}/pay`)
    } finally {
      executing.value = false
    }
  }

  return {
    history,
    historyLoading,
    historyError,
    executing,
    getPaymentHistory,
    getPendingEvent,
    executeRecurringPayment,
  }
}

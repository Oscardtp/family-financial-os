import { ref } from 'vue'
import api from '@/services/api'

export function useRecurringPayments() {
  const history = ref([])
  const historyLoading = ref(false)
  const historyError = ref(null)

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

  return {
    history,
    historyLoading,
    historyError,
    getPaymentHistory,
  }
}

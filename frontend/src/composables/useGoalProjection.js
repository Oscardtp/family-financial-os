import { ref } from 'vue'
import api from '@/services/api'

export function useGoalProjection() {
  const loading = ref(false)
  const error = ref(null)
  const projection = ref(null)

  async function calculateProjection(payload) {
    loading.value = true
    error.value = null
    try {
      const res = await api.post('/savings/goals/projection', payload)
      projection.value = res.data
      return res.data
    } catch (e) {
      error.value = 'No pudimos calcular la proyección. Intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, projection, calculateProjection }
}

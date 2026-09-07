import { ref } from 'vue'
import { useToast } from './useToast'

export function useApiError() {
  const loading = ref(false)
  const error = ref(null)
  const toast = useToast()

  function handleError(err, customMessage = null) {
    console.error('API Error:', err)

    let message = customMessage || 'Algo salió mal'

    if (err.response) {
      const status = err.response.status
      const data = err.response.data

      switch (status) {
        case 400:
          message = data?.detail || 'Revisa los datos e inténtalo de nuevo'
          break
        case 401:
          message = 'Sesión expirada. Inicia sesión de nuevo'
          break
        case 403:
          message = 'No tienes permiso para esta acción'
          break
        case 404:
          message = 'No encontramos esto'
          break
        case 422:
          message = data?.detail || 'Revisa los campos marcados'
          break
        case 500:
          message = 'Algo falló por aquí. Intenta más tarde'
          break
        default:
          message = data?.detail || 'Algo salió mal'
      }
    } else if (err.request) {
      message = 'Sin conexión a internet'
    }

    error.value = message
    toast.error(message)
    return message
  }

  function clearError() {
    error.value = null
  }

  function startLoading() {
    loading.value = true
    error.value = null
  }

  function stopLoading() {
    loading.value = false
  }

  async function withLoading(fn) {
    startLoading()
    try {
      const result = await fn()
      return result
    } catch (err) {
      handleError(err)
      throw err
    } finally {
      stopLoading()
    }
  }

  return {
    loading,
    error,
    handleError,
    clearError,
    startLoading,
    stopLoading,
    withLoading,
  }
}

import { ref } from 'vue'

const confirmState = ref({
  show: false,
  title: 'Confirmar',
  message: '',
  type: 'warning',
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  loading: false,
  resolve: null,
})

export function useConfirm() {
  function confirm({ title = 'Confirmar', message = '', type = 'warning', confirmText = 'Confirmar', cancelText = 'Cancelar' } = {}) {
    return new Promise((resolve) => {
      confirmState.value = {
        show: true,
        title,
        message,
        type,
        confirmText,
        cancelText,
        loading: false,
        resolve,
      }
    })
  }

  function handleConfirm() {
    confirmState.value.loading = true
    confirmState.value.resolve?.(true)
    confirmState.value.show = false
    confirmState.value.loading = false
  }

  function handleCancel() {
    confirmState.value.resolve?.(false)
    confirmState.value.show = false
  }

  return {
    confirmState,
    confirm,
    handleConfirm,
    handleCancel,
  }
}

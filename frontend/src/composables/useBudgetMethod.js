import { ref } from 'vue'
import api from '@/services/api'

export function useBudgetMethod() {
  const presets = ref([])
  const presetsLoading = ref(false)
  const config = ref(null)
  const configLoading = ref(false)
  const methodSaving = ref(false)
  const preview = ref(null)
  const previewLoading = ref(false)
  const methodError = ref('')

  async function loadPresets() {
    presetsLoading.value = true
    try {
      const { data } = await api.get('/budget-methods/presets')
      presets.value = data || []
    } catch {
      presets.value = []
    } finally {
      presetsLoading.value = false
    }
  }

  async function loadConfig() {
    configLoading.value = true
    methodError.value = ''
    try {
      const { data } = await api.get('/budget-method')
      config.value = data
      return data
    } catch {
      config.value = null
      return null
    } finally {
      configLoading.value = false
    }
  }

  async function saveConfig(payload) {
    methodSaving.value = true
    methodError.value = ''
    try {
      const { data } = await api.put('/budget-method', payload)
      config.value = data
      return data
    } finally {
      methodSaving.value = false
    }
  }

  async function fetchPreview(incomeAmount, groups) {
    previewLoading.value = true
    try {
      const { data } = await api.post('/budget-method/preview', {
        income_amount: String(incomeAmount),
        groups: groups.map((g) => ({ key: g.key, label: g.label, pct: Number(g.pct) })),
      })
      preview.value = data
      return data
    } finally {
      previewLoading.value = false
    }
  }

  function resetPreview() {
    preview.value = null
  }

  return {
    presets,
    presetsLoading,
    config,
    configLoading,
    methodSaving,
    preview,
    previewLoading,
    methodError,
    loadPresets,
    loadConfig,
    saveConfig,
    fetchPreview,
    resetPreview,
  }
}

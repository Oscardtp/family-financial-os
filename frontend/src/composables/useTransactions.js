import { ref, computed } from 'vue'
import api from '@/services/api'

export function useTransactions() {
  const transactions = ref([])
  const accounts = ref([])
  const categories = ref([])
  const loading = ref(true)
  const error = ref('')

  const incomeCategories = computed(() => categories.value.filter(c => c.type === 'income'))
  const expenseCategories = computed(() => categories.value.filter(c => c.type === 'expense'))

  async function loadData() {
    loading.value = true
    error.value = ''
    try {
      const [txRes, accRes, catRes] = await Promise.all([
        api.get('/transactions'),
        api.get('/accounts'),
        api.get('/categories'),
      ])
      transactions.value = txRes.data
      accounts.value = accRes.data
      categories.value = catRes.data
    } catch {
      error.value = 'No pudimos cargar tus datos. Intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  async function createTransaction(payload) {
    const { data } = await api.post('/transactions', payload)
    transactions.value.unshift(data)
    return data
  }

  async function deleteTransaction(id) {
    await api.delete(`/transactions/${id}`)
    transactions.value = transactions.value.filter(t => t.id !== id)
  }

  async function exportCSV() {
    const { data } = await api.get('/reports/transactions/csv', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'transacciones.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }

  return {
    transactions, accounts, categories, loading, error,
    incomeCategories, expenseCategories,
    loadData, createTransaction, deleteTransaction, exportCSV,
  }
}

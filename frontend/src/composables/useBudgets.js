import { ref, computed, reactive } from 'vue'
import api from '@/services/api'

export function useBudgets() {
  const now = new Date()
  const loading = ref(true)
  const error = ref('')
  const month = ref(now.getMonth() + 1)
  const year = ref(now.getFullYear())
  const statusData = ref(null)
  const rawBudgets = ref([])
  const categories = ref([])

  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
  ]
  const monthLabel = computed(() => `${monthNames[month.value - 1]} ${year.value}`)
  const budgetItems = computed(() => statusData.value?.items || [])

  const unbudgetedCategories = computed(() => {
    const budgetedIds = budgetItems.value.map(b => b.category_id)
    return categories.value.filter(c => c.type === 'expense' && !budgetedIds.includes(c.id))
  })

  const chartData = computed(() => {
    const items = budgetItems.value
    if (!items.length) return null
    return {
      labels: items.map(i => i.category),
      datasets: [
        { label: 'Presupuesto', data: items.map(i => i.budgeted), backgroundColor: '#3b82f6', borderRadius: 4 },
        { label: 'Gasto Real', data: items.map(i => i.spent), backgroundColor: items.map(i => i.status === 'over' ? '#ef4444' : '#22c55e'), borderRadius: 4 },
      ],
    }
  })

  const chartOptions = {
    plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 8 } } },
    scales: { y: { beginAtZero: true, ticks: { callback: v => '$' + Number(v).toLocaleString('es-CO', { maximumFractionDigits: 0 }) } }, x: { grid: { display: false } } },
  }

  function prevMonth() {
    if (month.value === 1) { month.value = 12; year.value-- }
    else { month.value-- }
    loadBudgets()
  }

  function nextMonth() {
    if (month.value === 12) { month.value = 1; year.value++ }
    else { month.value++ }
    loadBudgets()
  }

  function statusLabel(status) {
    const map = { ok: 'Vamos bien', warning: 'Cuidado', over: 'Nos pasamos' }
    return map[status] || status
  }

  async function loadBudgets() {
    loading.value = true
    error.value = ''
    try {
      const [statusRes, rawRes] = await Promise.all([
        api.get('/budgets/status', { params: { month: month.value, year: year.value } }),
        api.get('/budgets', { params: { month: month.value, year: year.value } }),
      ])
      statusData.value = statusRes.data
      rawBudgets.value = rawRes.data
    } catch {
      error.value = 'No pudimos cargar tus presupuestos. Intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  async function loadCategories() {
    try {
      const { data } = await api.get('/categories')
      categories.value = data
    } catch { /* empty */ }
  }

  async function createBudget(payload) {
    await api.post('/budgets', payload)
    await loadBudgets()
  }

  async function editBudget(id, amount) {
    await api.put(`/budgets/${id}`, { amount })
    await loadBudgets()
  }

  async function deleteBudget(id) {
    await api.delete(`/budgets/${id}`)
    await loadBudgets()
  }

  return {
    loading, error, month, year, monthLabel, statusData, rawBudgets,
    budgetItems, unbudgetedCategories, chartData, chartOptions,
    prevMonth, nextMonth, statusLabel, loadBudgets, loadCategories,
    createBudget, editBudget, deleteBudget,
  }
}

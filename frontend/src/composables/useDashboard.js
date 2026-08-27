import { ref, computed } from 'vue'
import api from '@/services/api'

const barColors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']

export function useDashboard() {
  const loading = ref(true)
  const error = ref('')
  const d = ref({
    total_balance: 0, monthly_income: 0, monthly_expenses: 0,
    net_monthly: 0, total_debt: 0, total_savings: 0,
    net_worth: 0, recent_transactions: [], budget_status: [],
    savings_summary: null, upcoming_payments: [], monthly_payments: [],
  })
  const debts = ref([])

  const topCategories = computed(() => {
    const budgets = d.value.budget_status
    if (!budgets?.length) return []
    const total = budgets.reduce((s, b) => s + b.spent, 0)
    return budgets
      .filter(b => b.spent > 0)
      .sort((a, b) => b.spent - a.spent)
      .slice(0, 6)
      .map((b, i) => ({
        name: b.category,
        icon: b.category_icon || '📦',
        amount: b.spent,
        pct: total > 0 ? (b.spent / total) * 100 : 0,
        color: barColors[i % barColors.length],
      }))
  })

  const upcomingPayments = computed(() => d.value.upcoming_payments || [])
  const monthlyPayments = computed(() => d.value.monthly_payments || [])
  const totalMonthlyPaid = computed(() => monthlyPayments.value.reduce((sum, p) => sum + (p.amount || 0), 0))
  const totalMonthlyPayment = computed(() => debts.value.filter(x => x.status === 'active').reduce((sum, x) => sum + (x.minimum_payment || 0), 0))
  const totalDebts = computed(() => debts.value.filter(x => x.status === 'active').length)
  const paidCount = computed(() => debts.value.filter(x => x.status === 'active' && x.current_balance <= 0).length)

  async function loadData() {
    loading.value = true
    error.value = ''
    try {
      const [dashboardRes, debtsRes] = await Promise.all([
        api.get('/dashboard'),
        api.get('/debts'),
      ])
      d.value = dashboardRes.data
      debts.value = debtsRes.data
    } catch {
      error.value = 'No pudimos cargar tu panel. Revisa tu conexión e intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  return {
    loading, error, d, debts,
    topCategories, upcomingPayments, monthlyPayments,
    totalMonthlyPaid, totalMonthlyPayment, totalDebts, paidCount,
    loadData,
  }
}

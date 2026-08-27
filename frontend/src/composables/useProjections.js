import { ref, computed } from 'vue'
import api from '@/services/api'

export function useProjections() {
  const loading = ref(true)
  const error = ref('')
  const cashFlow = ref({ months: 12, projections: [], projected_savings: 0 })
  const debtProjections = ref({ debts: [] })
  const savingsProjection = ref({ goals: [], total_target: 0, total_current: 0, overall_percentage: 0 })
  const scenarioResult = ref(null)
  const scenarioLoading = ref(false)

  const scenarioForm = ref({
    income_change: 0, expense_change: 0,
    extra_debt: 0, new_savings: 0, months: 12,
  })

  const maxCashFlow = computed(() => {
    const vals = (cashFlow.value.projections || []).flatMap(p => [p.income, p.expenses])
    return Math.max(...vals, 1)
  })

  const maxScenario = computed(() => {
    const vals = (scenarioResult.value?.projections || []).flatMap(p => [p.income, p.expenses, p.debt_payment])
    return Math.max(...vals, 1)
  })

  function barWidth(val, max) { return max > 0 ? (val / max) * 100 : 0 }

  async function loadData() {
    loading.value = true
    error.value = ''
    try {
      const [cf, dp, sp] = await Promise.all([
        api.get('/projections/cash-flow?months=12'),
        api.get('/projections/debts'),
        api.get('/projections/savings?months=12'),
      ])
      cashFlow.value = cf.data
      debtProjections.value = dp.data
      savingsProjection.value = sp.data
    } catch {
      error.value = 'No pudimos cargar las proyecciones. Intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  async function runScenario() {
    scenarioLoading.value = true
    try {
      const params = new URLSearchParams({
        monthly_income_change: scenarioForm.value.income_change,
        monthly_expense_change: scenarioForm.value.expense_change,
        extra_debt_payment: scenarioForm.value.extra_debt,
        new_monthly_savings: scenarioForm.value.new_savings,
        months: scenarioForm.value.months,
      })
      const { data } = await api.post(`/projections/scenario?${params}`)
      scenarioResult.value = data
    } catch { /* empty */ }
    scenarioLoading.value = false
  }

  return {
    loading, error, cashFlow, debtProjections, savingsProjection,
    scenarioResult, scenarioLoading, scenarioForm,
    maxCashFlow, maxScenario, barWidth,
    loadData, runScenario,
  }
}

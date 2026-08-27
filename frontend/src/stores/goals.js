import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { useCurrency } from '@/composables/useCurrency'

export const useGoalsStore = defineStore('goals', () => {
  const { fmt, fmtFull, fmtDate, fmtMonth } = useCurrency()

  const goals = ref([])
  const loading = ref(false)
  const error = ref(null)
  const expandedGoal = ref(null)
  const highlightedGoalId = ref(null)
  const filterType = ref('all')
  const sortBy = ref('name')

  const activeGoals = computed(() => {
    let filtered = goals.value.filter(g => g.current_amount < g.target_amount)

    if (filterType.value !== 'all') {
      filtered = filtered.filter(g => g.goal_type === filterType.value)
    }

    const priorityOrder = { high: 0, medium: 1, low: 2 }
    return filtered.sort((a, b) => {
      switch (sortBy.value) {
        case 'priority': return (priorityOrder[a.priority] ?? 1) - (priorityOrder[b.priority] ?? 1)
        case 'progress': return goalProgress(b) - goalProgress(a)
        case 'date': return (a.target_date || 'z').localeCompare(b.target_date || 'z')
        default: return a.name.localeCompare(b.name)
      }
    })
  })

  const completedGoals = computed(() =>
    goals.value.filter(g => g.current_amount >= g.target_amount)
  )

  const totalCurrent = computed(() =>
    goals.value.reduce((sum, g) => sum + (g.current_amount || 0), 0)
  )

  const totalTarget = computed(() =>
    goals.value.reduce((sum, g) => sum + (g.target_amount || 0), 0)
  )

  const overallProgress = computed(() => {
    if (!totalTarget.value) return 0
    return Math.round((totalCurrent.value / totalTarget.value) * 100)
  })

  function goalProgress(goal) {
    if (!goal.target_amount) return 0
    return Math.round((goal.current_amount / goal.target_amount) * 100)
  }

  function monthsRemaining(goal) {
    if (!goal.target_date) return null
    const target = new Date(goal.target_date)
    const now = new Date()
    const months = (target.getFullYear() - now.getFullYear()) * 12 + (target.getMonth() - now.getMonth())
    return months > 0 ? months : null
  }

  async function fetchGoals() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/savings/goals')
      goals.value = res.data
    } catch {
      error.value = 'No pudimos cargar tus metas. Revisa tu conexión e intenta de nuevo.'
    } finally {
      loading.value = false
    }
  }

  async function createGoal(data) {
    try {
      const payload = {
        name: data.name,
        target_amount: parseFloat(data.target_amount),
        priority: data.priority,
        goal_type: data.goal_type,
      }
      if (data.monthly_contribution) payload.monthly_contribution = parseFloat(data.monthly_contribution)
      if (data.target_date) payload.target_date = data.target_date
      if (data.goal_type === 'investment') {
        if (data.expected_return_rate) payload.expected_return_rate = parseFloat(data.expected_return_rate)
        if (data.horizon_months) payload.horizon_months = parseInt(data.horizon_months)
      }
      await api.post('/savings/goals', payload)
      await fetchGoals()
      return { error: null }
    } catch {
      return { error: 'No pudimos crear la meta. Intenta de nuevo.' }
    }
  }

  async function editGoal(id, data) {
    try {
      const payload = {
        name: data.name,
        target_amount: parseFloat(data.target_amount),
        priority: data.priority,
        goal_type: data.goal_type,
      }
      if (data.monthly_contribution) payload.monthly_contribution = parseFloat(data.monthly_contribution)
      if (data.target_date) payload.target_date = data.target_date
      await api.put(`/savings/goals/${id}`, payload)
      await fetchGoals()
      return { error: null }
    } catch {
      return { error: 'No pudimos guardar los cambios. Intenta de nuevo.' }
    }
  }

  async function deleteGoal(id) {
    try {
      await api.delete(`/savings/goals/${id}`)
      expandedGoal.value = null
      await fetchGoals()
      return { error: null }
    } catch {
      return { error: 'No pudimos eliminar la meta. Intenta de nuevo.' }
    }
  }

  async function contributeGoal(id, amount, date) {
    try {
      await api.post(`/savings/goals/${id}/contributions`, {
        amount: parseFloat(amount),
        contribution_date: date,
      })
      const goal = goals.value.find(g => g.id === id)
      if (goal) goal.current_amount += parseFloat(amount)
      setTimeout(() => fetchGoals(), 600)
      return { error: null }
    } catch {
      return { error: 'No pudimos registrar el aporte. Intenta de nuevo.' }
    }
  }

  async function loadGoalHistory(goal) {
    try {
      const res = await api.get(`/savings/goals/${goal.id}/contributions`)
      goal.history = res.data
    } catch {
      goal.history = []
    }
  }

  return {
    goals,
    loading,
    error,
    expandedGoal,
    highlightedGoalId,
    filterType,
    sortBy,
    activeGoals,
    completedGoals,
    totalCurrent,
    totalTarget,
    overallProgress,
    goalProgress,
    monthsRemaining,
    fetchGoals,
    createGoal,
    editGoal,
    deleteGoal,
    contributeGoal,
    loadGoalHistory,
    fmt,
    fmtFull,
    fmtDate,
    fmtMonth,
  }
})

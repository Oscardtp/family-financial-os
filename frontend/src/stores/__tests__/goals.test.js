import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useGoalsStore } from '../goals'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${v}`,
    fmtFull: (v) => `$${v} COP`,
    fmtDate: (d) => d,
    fmtMonth: (d) => d,
  }),
}))

import api from '@/services/api'

function makeGoal(overrides = {}) {
  return {
    id: 'g1',
    name: 'Vacaciones',
    goal_type: 'savings',
    priority: 'medium',
    target_amount: 5000000,
    current_amount: 1000000,
    monthly_contribution: 500000,
    target_date: '2026-12-31',
    ...overrides,
  }
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
})

describe('useGoalsStore', () => {
  describe('state', () => {
    it('initializes with empty goals', () => {
      const store = useGoalsStore()
      expect(store.goals).toEqual([])
    })

    it('initializes loading as false', () => {
      const store = useGoalsStore()
      expect(store.loading).toBe(false)
    })

    it('initializes error as null', () => {
      const store = useGoalsStore()
      expect(store.error).toBeNull()
    })

    it('initializes filterType as all', () => {
      const store = useGoalsStore()
      expect(store.filterType).toBe('all')
    })

    it('initializes sortBy as name', () => {
      const store = useGoalsStore()
      expect(store.sortBy).toBe('name')
    })
  })

  describe('activeGoals', () => {
    it('filters completed goals', () => {
      const store = useGoalsStore()
      store.goals = [
        makeGoal({ id: 'g1', current_amount: 1000000 }),
        makeGoal({ id: 'g2', current_amount: 5000000, target_amount: 5000000 }),
      ]
      expect(store.activeGoals).toHaveLength(1)
      expect(store.activeGoals[0].id).toBe('g1')
    })

    it('filters by goal_type when set', () => {
      const store = useGoalsStore()
      store.filterType = 'savings'
      store.goals = [
        makeGoal({ id: 'g1', goal_type: 'savings' }),
        makeGoal({ id: 'g2', goal_type: 'investment' }),
      ]
      expect(store.activeGoals).toHaveLength(1)
      expect(store.activeGoals[0].id).toBe('g1')
    })

    it('shows all types when filter is all', () => {
      const store = useGoalsStore()
      store.filterType = 'all'
      store.goals = [
        makeGoal({ id: 'g1', goal_type: 'savings' }),
        makeGoal({ id: 'g2', goal_type: 'investment' }),
      ]
      expect(store.activeGoals).toHaveLength(2)
    })

    it('sorts by priority', () => {
      const store = useGoalsStore()
      store.sortBy = 'priority'
      store.goals = [
        makeGoal({ id: 'g1', priority: 'low' }),
        makeGoal({ id: 'g2', priority: 'high' }),
        makeGoal({ id: 'g3', priority: 'medium' }),
      ]
      expect(store.activeGoals.map(g => g.id)).toEqual(['g2', 'g3', 'g1'])
    })

    it('sorts by progress descending', () => {
      const store = useGoalsStore()
      store.sortBy = 'progress'
      store.goals = [
        makeGoal({ id: 'g1', current_amount: 1000000, target_amount: 5000000 }),
        makeGoal({ id: 'g2', current_amount: 4000000, target_amount: 5000000 }),
      ]
      expect(store.activeGoals.map(g => g.id)).toEqual(['g2', 'g1'])
    })

    it('sorts by date ascending', () => {
      const store = useGoalsStore()
      store.sortBy = 'date'
      store.goals = [
        makeGoal({ id: 'g1', target_date: '2026-12-31' }),
        makeGoal({ id: 'g2', target_date: '2026-06-15' }),
      ]
      expect(store.activeGoals.map(g => g.id)).toEqual(['g2', 'g1'])
    })

    it('sorts by name by default', () => {
      const store = useGoalsStore()
      store.goals = [
        makeGoal({ id: 'g1', name: 'Zebra' }),
        makeGoal({ id: 'g2', name: 'Alpha' }),
      ]
      expect(store.activeGoals.map(g => g.id)).toEqual(['g2', 'g1'])
    })
  })

  describe('completedGoals', () => {
    it('returns goals where current >= target', () => {
      const store = useGoalsStore()
      store.goals = [
        makeGoal({ id: 'g1', current_amount: 5000000, target_amount: 5000000 }),
        makeGoal({ id: 'g2', current_amount: 1000000, target_amount: 5000000 }),
      ]
      expect(store.completedGoals).toHaveLength(1)
      expect(store.completedGoals[0].id).toBe('g1')
    })
  })

  describe('aggregates', () => {
    it('totalCurrent sums current_amount', () => {
      const store = useGoalsStore()
      store.goals = [
        makeGoal({ current_amount: 1000000 }),
        makeGoal({ id: 'g2', current_amount: 2000000 }),
      ]
      expect(store.totalCurrent).toBe(3000000)
    })

    it('totalTarget sums target_amount', () => {
      const store = useGoalsStore()
      store.goals = [
        makeGoal({ target_amount: 5000000 }),
        makeGoal({ id: 'g2', target_amount: 3000000 }),
      ]
      expect(store.totalTarget).toBe(8000000)
    })

    it('overallProgress calculates percentage', () => {
      const store = useGoalsStore()
      store.goals = [
        makeGoal({ current_amount: 5000000, target_amount: 10000000 }),
      ]
      expect(store.overallProgress).toBe(50)
    })

    it('overallProgress returns 0 when no targets', () => {
      const store = useGoalsStore()
      store.goals = []
      expect(store.overallProgress).toBe(0)
    })
  })

  describe('helpers', () => {
    it('goalProgress calculates percentage', () => {
      const store = useGoalsStore()
      const goal = makeGoal({ current_amount: 2500000, target_amount: 5000000 })
      expect(store.goalProgress(goal)).toBe(50)
    })

    it('goalProgress returns 0 for zero target', () => {
      const store = useGoalsStore()
      const goal = makeGoal({ current_amount: 1000000, target_amount: 0 })
      expect(store.goalProgress(goal)).toBe(0)
    })

    it('monthsRemaining calculates months', () => {
      const store = useGoalsStore()
      const future = new Date()
      future.setMonth(future.getMonth() + 6)
      const goal = makeGoal({ target_date: future.toISOString().split('T')[0] })
      expect(store.monthsRemaining(goal)).toBe(6)
    })

    it('monthsRemaining returns null for past dates', () => {
      const store = useGoalsStore()
      const goal = makeGoal({ target_date: '2020-01-01' })
      expect(store.monthsRemaining(goal)).toBeNull()
    })

    it('monthsRemaining returns null when no target_date', () => {
      const store = useGoalsStore()
      const goal = makeGoal({ target_date: null })
      expect(store.monthsRemaining(goal)).toBeNull()
    })
  })

  describe('fetchGoals', () => {
    it('sets goals array on success', async () => {
      const goals = [makeGoal(), makeGoal({ id: 'g2' })]
      api.get.mockResolvedValue({ data: goals })
      const store = useGoalsStore()
      await store.fetchGoals()
      expect(store.goals).toEqual(goals)
      expect(store.loading).toBe(false)
    })

    it('sets error on failure', async () => {
      api.get.mockRejectedValue(new Error('Network'))
      const store = useGoalsStore()
      await store.fetchGoals()
      expect(store.error).toContain('metas')
      expect(store.loading).toBe(false)
    })
  })

  describe('createGoal', () => {
    it('calls API and refetches goals', async () => {
      api.post.mockResolvedValue({})
      api.get.mockResolvedValue({ data: [makeGoal()] })
      const store = useGoalsStore()
      const result = await store.createGoal({
        name: 'Vacaciones',
        target_amount: '5000000',
        priority: 'medium',
        goal_type: 'savings',
      })
      expect(result.error).toBeNull()
      expect(api.post).toHaveBeenCalledWith('/savings/goals', expect.objectContaining({
        name: 'Vacaciones',
        target_amount: 5000000,
      }))
      expect(api.get).toHaveBeenCalled()
    })

    it('returns error on failure', async () => {
      api.post.mockRejectedValue(new Error('fail'))
      const store = useGoalsStore()
      const result = await store.createGoal({
        name: 'Fallo',
        target_amount: '1000',
        priority: 'low',
        goal_type: 'savings',
      })
      expect(result.error).toContain('crear')
    })
  })

  describe('editGoal', () => {
    it('calls API with correct id and payload', async () => {
      api.put.mockResolvedValue({})
      api.get.mockResolvedValue({ data: [] })
      const store = useGoalsStore()
      const result = await store.editGoal('g1', {
        name: 'Editado',
        target_amount: '3000000',
        priority: 'high',
        goal_type: 'savings',
      })
      expect(result.error).toBeNull()
      expect(api.put).toHaveBeenCalledWith('/savings/goals/g1', expect.objectContaining({
        name: 'Editado',
        target_amount: 3000000,
      }))
    })

    it('returns error on failure', async () => {
      api.put.mockRejectedValue(new Error('fail'))
      const store = useGoalsStore()
      const result = await store.editGoal('g1', {
        name: 'X', target_amount: '1', priority: 'low', goal_type: 'savings',
      })
      expect(result.error).toContain('guardar')
    })
  })

  describe('deleteGoal', () => {
    it('calls API and clears expandedGoal', async () => {
      api.delete.mockResolvedValue({})
      api.get.mockResolvedValue({ data: [] })
      const store = useGoalsStore()
      store.expandedGoal = 'g1'
      const result = await store.deleteGoal('g1')
      expect(result.error).toBeNull()
      expect(api.delete).toHaveBeenCalledWith('/savings/goals/g1')
      expect(store.expandedGoal).toBeNull()
    })

    it('returns error on failure', async () => {
      api.delete.mockRejectedValue(new Error('fail'))
      const store = useGoalsStore()
      const result = await store.deleteGoal('g1')
      expect(result.error).toContain('eliminar')
    })
  })

  describe('contributeGoal', () => {
    it('calls API and optimistically updates current_amount', async () => {
      api.post.mockResolvedValue({})
      api.get.mockResolvedValue({ data: [] })
      const store = useGoalsStore()
      store.goals = [makeGoal({ id: 'g1', current_amount: 1000000 })]
      const result = await store.contributeGoal('g1', 500000, '2026-08-27')
      expect(result.error).toBeNull()
      expect(api.post).toHaveBeenCalledWith('/savings/goals/g1/contributions', {
        amount: 500000,
        contribution_date: '2026-08-27',
      })
      expect(store.goals[0].current_amount).toBe(1500000)
    })

    it('returns error on failure', async () => {
      api.post.mockRejectedValue(new Error('fail'))
      const store = useGoalsStore()
      const result = await store.contributeGoal('g1', 500000, '2026-08-27')
      expect(result.error).toContain('aporte')
    })
  })

  describe('loadGoalHistory', () => {
    it('sets goal.history on success', async () => {
      api.get.mockResolvedValue({ data: [{ date: '2026-08-01', amount: 100000 }] })
      const store = useGoalsStore()
      const goal = makeGoal()
      await store.loadGoalHistory(goal)
      expect(goal.history).toEqual([{ date: '2026-08-01', amount: 100000 }])
    })

    it('sets empty array on failure', async () => {
      api.get.mockRejectedValue(new Error('fail'))
      const store = useGoalsStore()
      const goal = makeGoal()
      await store.loadGoalHistory(goal)
      expect(goal.history).toEqual([])
    })
  })
})

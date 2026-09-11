import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GoalScenarioSimulator from '../GoalScenarioSimulator.vue'

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${v}`,
  }),
}))

vi.mock('@/composables/useGoalProjection', () => ({
  useGoalProjection: () => ({
    calculateProjection: vi.fn().mockResolvedValue({
      projected_value: 6000000,
      total_contributions: 5500000,
      total_interest: 500000,
      months_to_goal: 10,
    }),
    loading: { value: false },
  }),
}))

const makeGoal = (overrides = {}) => ({
  id: 'g1',
  name: 'Vacaciones',
  goal_type: 'investment',
  target_amount: 5000000,
  current_amount: 1000000,
  monthly_contribution: 500000,
  expected_return_rate: 9,
  horizon_months: 24,
  ...overrides,
})

describe('GoalScenarioSimulator', () => {
  it('renders title', () => {
    const wrapper = mount(GoalScenarioSimulator, {
      props: { goal: makeGoal() },
    })
    expect(wrapper.text()).toContain('¿Qué pasa si ahorro más al mes?')
  })

  it('shows presets', () => {
    const wrapper = mount(GoalScenarioSimulator, {
      props: { goal: makeGoal() },
    })
    expect(wrapper.findAll('.preset-btn')).toHaveLength(4)
  })

  it('disables simulate button when goal has no target', () => {
    const wrapper = mount(GoalScenarioSimulator, {
      props: { goal: makeGoal({ target_amount: 0 }) },
    })
    expect(wrapper.find('.simulate-btn').attributes('disabled')).toBeDefined()
  })
})

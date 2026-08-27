import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GoalCard from '../GoalCard.vue'

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${v}`,
    fmtMonth: (d) => d,
  }),
}))

vi.mock('lucide-vue-next', () => ({
  Calendar: { template: '<span />' },
  TrendingUp: { template: '<span />' },
}))

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

function mountCard(props = {}) {
  return mount(GoalCard, {
    props: {
      goal: makeGoal(),
      ...props,
    },
    global: {
      stubs: {
        Calendar: { template: '<span />' },
        TrendingUp: { template: '<span />' },
      },
    },
  })
}

describe('GoalCard', () => {
  it('renders goal name', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.goal-name').text()).toBe('Vacaciones')
  })

  it('renders savings type badge', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.goal-type-badge').text()).toBe('Ahorro')
  })

  it('renders investment type badge', () => {
    const wrapper = mountCard({ goal: makeGoal({ goal_type: 'investment' }) })
    expect(wrapper.find('.goal-type-badge').text()).toBe('Inversión')
  })

  it('renders completed badge when completed', () => {
    const wrapper = mountCard({
      completed: true,
      goal: makeGoal({ current_amount: 5000000 }),
    })
    expect(wrapper.find('.goal-type-badge').text()).toBe('Lograda')
  })

  it('renders priority badge', () => {
    const wrapper = mountCard({ goal: makeGoal({ priority: 'high' }) })
    expect(wrapper.find('.priority-badge').text()).toBe('Alta')
  })

  it('renders medium priority', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.priority-badge').text()).toBe('Media')
  })

  it('renders low priority', () => {
    const wrapper = mountCard({ goal: makeGoal({ priority: 'low' }) })
    expect(wrapper.find('.priority-badge').text()).toBe('Baja')
  })

  it('does not render priority badge when completed', () => {
    const wrapper = mountCard({
      completed: true,
      goal: makeGoal({ current_amount: 5000000, priority: 'high' }),
    })
    expect(wrapper.find('.priority-badge').exists()).toBe(false)
  })

  it('shows progress percentage', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.progress-pct').text()).toBe('20%')
  })

  it('shows amounts (current, target, remaining)', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.amount-current').text()).toContain('1000000')
    expect(wrapper.find('.amount-target').text()).toContain('5000000')
    expect(wrapper.find('.amount-remaining').text()).toContain('4000000')
  })

  it('shows monthly contribution', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.goal-monthly').exists()).toBe(true)
    expect(wrapper.find('.monthly-value').text()).toContain('500000')
  })

  it('hides monthly contribution when not set', () => {
    const wrapper = mountCard({ goal: makeGoal({ monthly_contribution: null }) })
    expect(wrapper.find('.goal-monthly').exists()).toBe(false)
  })

  it('shows target date', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.goal-timeline').text()).toContain('2026-12-31')
  })

  it('hides target date when not set', () => {
    const wrapper = mountCard({ goal: makeGoal({ target_date: null }) })
    expect(wrapper.find('.goal-timeline').exists()).toBe(false)
  })

  it('shows investment projection details', () => {
    const wrapper = mountCard({
      goal: makeGoal({
        goal_type: 'investment',
        expected_return_rate: 9,
        horizon_months: 24,
      }),
    })
    expect(wrapper.find('.goal-projection').exists()).toBe(true)
    expect(wrapper.find('.goal-projection').text()).toContain('9%')
    expect(wrapper.find('.goal-projection').text()).toContain('24 meses')
  })

  it('hides projection for savings goals', () => {
    const wrapper = mountCard()
    expect(wrapper.find('.goal-projection').exists()).toBe(false)
  })

  it('emits contribute on button click', async () => {
    const wrapper = mountCard()
    await wrapper.find('.action-btn.primary').trigger('click')
    expect(wrapper.emitted('contribute')).toHaveLength(1)
    expect(wrapper.emitted('contribute')[0][0]).toEqual(makeGoal())
  })

  it('emits toggle-expand on button click', async () => {
    const wrapper = mountCard()
    await wrapper.find('.action-btn.secondary').trigger('click')
    expect(wrapper.emitted('toggle-expand')).toHaveLength(1)
  })

  it('shows "Ver detalles" when collapsed', () => {
    const wrapper = mountCard({ expanded: false })
    expect(wrapper.find('.action-btn.secondary').text()).toBe('Ver detalles')
  })

  it('shows "Cerrar" when expanded', () => {
    const wrapper = mountCard({ expanded: true })
    expect(wrapper.find('.action-btn.secondary').text()).toBe('Cerrar')
  })

  it('shows edit/delete buttons when expanded', () => {
    const wrapper = mountCard({ expanded: true })
    expect(wrapper.find('.expanded-btn').exists()).toBe(true)
    expect(wrapper.findAll('.expanded-btn')).toHaveLength(2)
  })

  it('hides expanded section when not expanded', () => {
    const wrapper = mountCard({ expanded: false })
    expect(wrapper.find('.goal-expanded').exists()).toBe(false)
  })

  it('emits edit on edit button click', async () => {
    const wrapper = mountCard({ expanded: true })
    await wrapper.find('.expanded-btn').trigger('click')
    expect(wrapper.emitted('edit')).toHaveLength(1)
  })

  it('emits delete on delete button click', async () => {
    const wrapper = mountCard({ expanded: true })
    await wrapper.find('.expanded-btn.danger').trigger('click')
    expect(wrapper.emitted('delete')).toHaveLength(1)
  })

  it('shows empty history message when no history', () => {
    const wrapper = mountCard({
      expanded: true,
      goal: makeGoal({ history: [] }),
    })
    expect(wrapper.find('.expanded-empty').text()).toContain('Aún no hay aportes')
  })

  it('renders completed state with 100% progress', () => {
    const wrapper = mountCard({
      completed: true,
      goal: makeGoal({ current_amount: 5000000, target_amount: 5000000 }),
    })
    expect(wrapper.find('.progress-pct').text()).toBe('100%')
    expect(wrapper.find('.completed-amount').text()).toContain('5000000')
  })

  it('applies highlight-new class when highlighted', () => {
    const wrapper = mountCard({ highlighted: true })
    expect(wrapper.find('.goal-card').classes()).toContain('highlight-new')
  })

  it('applies expanded class when expanded', () => {
    const wrapper = mountCard({ expanded: true })
    expect(wrapper.find('.goal-card').classes()).toContain('expanded')
  })

  it('applies completed class when completed', () => {
    const wrapper = mountCard({ completed: true })
    expect(wrapper.find('.goal-card').classes()).toContain('completed')
  })
})

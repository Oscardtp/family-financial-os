import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GoalMonthlyBreakdown from '../GoalMonthlyBreakdown.vue'

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${v}`,
  }),
}))

function makeBreakdown(overrides = {}) {
  return [
    { month: 'Ene 2026', contribution: 500000, interest: 10000, balance: 510000 },
    { month: 'Feb 2026', contribution: 500000, interest: 20000, balance: 1030000, ...overrides },
  ]
}

describe('GoalMonthlyBreakdown', () => {
  it('renders toggle button', () => {
    const wrapper = mount(GoalMonthlyBreakdown, {
      props: { monthlyBreakdown: makeBreakdown() },
    })
    expect(wrapper.find('.breakdown-toggle').exists()).toBe(true)
  })

  it('does not show table by default', () => {
    const wrapper = mount(GoalMonthlyBreakdown, {
      props: { monthlyBreakdown: makeBreakdown() },
    })
    expect(wrapper.find('.breakdown-table').exists()).toBe(false)
  })

  it('shows table when toggled', async () => {
    const wrapper = mount(GoalMonthlyBreakdown, {
      props: { monthlyBreakdown: makeBreakdown() },
    })
    await wrapper.find('.breakdown-toggle').trigger('click')
    expect(wrapper.find('.breakdown-table').exists()).toBe(true)
    expect(wrapper.findAll('.breakdown-table tbody tr')).toHaveLength(2)
  })
})

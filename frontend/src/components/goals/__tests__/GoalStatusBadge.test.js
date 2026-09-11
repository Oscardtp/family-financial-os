import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GoalStatusBadge from '../GoalStatusBadge.vue'

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${v}`,
    fmtMonth: (d) => d,
  }),
}))

describe('GoalStatusBadge', () => {
  it('renders Lograda when completed', () => {
    const wrapper = mount(GoalStatusBadge, { props: { completed: true } })
    expect(wrapper.text()).toBe('Lograda')
    expect(wrapper.find('.goal-status-badge').classes()).toContain('completed')
  })

  it('renders En buen camino when onTrack is true', () => {
    const wrapper = mount(GoalStatusBadge, { props: { onTrack: true } })
    expect(wrapper.text()).toBe('En buen camino')
    expect(wrapper.find('.goal-status-badge').classes()).toContain('on-track')
  })

  it('renders Revisa tu aporte when onTrack is false', () => {
    const wrapper = mount(GoalStatusBadge, { props: { onTrack: false } })
    expect(wrapper.text()).toBe('Revisa tu aporte')
    expect(wrapper.find('.goal-status-badge').classes()).toContain('at-risk')
  })

  it('renders Sin datos when onTrack is null', () => {
    const wrapper = mount(GoalStatusBadge, { props: { onTrack: null } })
    expect(wrapper.text()).toBe('Sin datos')
    expect(wrapper.find('.goal-status-badge').classes()).toContain('unknown')
  })
})

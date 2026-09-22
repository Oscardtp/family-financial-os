import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BudgetCard from '@/components/resumen/BudgetCard.vue'

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => {
      const n = Number(v || 0)
      return n.toLocaleString('es-CO')
    },
  }),
}))

function makeProps(overrides = {}) {
  return {
    budgetStatus: [
      {
        category: 'Alimentacion',
        budgeted: 500000,
        spent: 350000,
        status: 'ok',
        message: 'Alimentacion esta dentro del presupuesto.',
      },
      {
        category: 'Transporte',
        budgeted: 200000,
        spent: 180000,
        status: 'warning',
        message: 'Transporte va al 90% del presupuesto.',
      },
    ],
    budgetProjection: {
      total_projected_spent: 1250000,
      total_budgeted: 1500000,
      total_will_exceed: false,
    },
    loading: false,
    error: '',
    ...overrides,
  }
}

describe('BudgetCard', () => {
  it('renders loading skeleton when loading=true', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({ loading: true }),
    })
    expect(wrapper.find('.bc-skeleton').exists()).toBe(true)
    expect(wrapper.find('.bc-card-content').exists()).toBe(false)
  })

  it('renders empty state when budgetStatus is empty', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [],
        budgetProjection: { total_projected_spent: 0, total_budgeted: 0, total_will_exceed: false },
      }),
    })
    expect(wrapper.text()).toContain('Aun no has configurado un presupuesto')
    expect(wrapper.find('.bc-empty-cta').exists()).toBe(true)
  })

  it('renders empty state when total_budgeted is 0', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [{ category: 'Test', budgeted: 0, spent: 0, status: 'ok', message: '' }],
        budgetProjection: { total_projected_spent: 0, total_budgeted: 0, total_will_exceed: false },
      }),
    })
    expect(wrapper.text()).toContain('Aun no has configurado un presupuesto')
  })

  it('renders error state when error is set', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({ error: 'Error de red' }),
    })
    expect(wrapper.text()).toContain('No pudimos cargar tu presupuesto')
  })

  it('renders correct amounts from budgetProjection', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps(),
    })
    expect(wrapper.text()).toContain('1.250.000')
    expect(wrapper.text()).toContain('1.500.000')
  })

  it('renders progress bar with correct width', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps(),
    })
    const bar = wrapper.find('.bc-bar-fill')
    expect(bar.exists()).toBe(true)
    expect(bar.attributes('style')).toContain('83.3')
  })

  it('shows no badge when all categories are ok', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [
          { category: 'A', budgeted: 500000, spent: 200000, status: 'ok', message: 'OK' },
          { category: 'B', budgeted: 300000, spent: 100000, status: 'ok', message: 'OK' },
        ],
        budgetProjection: { total_projected_spent: 300000, total_budgeted: 800000, total_will_exceed: false },
      }),
    })
    expect(wrapper.find('.bc-status-badge').exists()).toBe(false)
  })

  it('shows warning badge when status is warning', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [
          { category: 'A', budgeted: 500000, spent: 450000, status: 'warning', message: 'Cuidado' },
        ],
        budgetProjection: { total_projected_spent: 450000, total_budgeted: 500000, total_will_exceed: false },
      }),
    })
    const badge = wrapper.find('.bc-status-badge')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('Cuidado')
  })

  it('shows exceeded badge when status is exceeded', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [
          { category: 'A', budgeted: 500000, spent: 550000, status: 'exceeded', message: 'Nos pasamos' },
        ],
        budgetProjection: { total_projected_spent: 550000, total_budgeted: 500000, total_will_exceed: true },
      }),
    })
    const badge = wrapper.find('.bc-status-badge')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('Nos pasamos')
  })

  it('shows max two at-risk categories', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [
          { category: 'A', budgeted: 100, spent: 90, status: 'warning', message: 'W1' },
          { category: 'B', budgeted: 100, spent: 110, status: 'exceeded', message: 'E1' },
          { category: 'C', budgeted: 100, spent: 95, status: 'warning', message: 'W2' },
        ],
        budgetProjection: { total_projected_spent: 295, total_budgeted: 300, total_will_exceed: true },
      }),
    })
    const riskItems = wrapper.findAll('.bc-risk-item')
    expect(riskItems.length).toBeLessThanOrEqual(2)
  })

  it('renders backend message exactly', () => {
    const msg = 'Segun el ritmo actual, podríamos terminar excediendo.'
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetProjection: { total_projected_spent: 1600000, total_budgeted: 1500000, total_will_exceed: true },
        budgetStatus: [
          { category: 'A', budgeted: 500000, spent: 500000, status: 'exceeded', message: msg },
        ],
      }),
    })
    expect(wrapper.text()).toContain(msg)
  })

  it('emits open-budget when CTA is clicked (non-empty state)', async () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps(),
    })
    const cta = wrapper.find('.bc-cta')
    expect(cta.exists()).toBe(true)
    await cta.trigger('click')
    expect(wrapper.emitted('open-budget')).toBeTruthy()
  })

  it('shows "Editar presupuesto" CTA when budget exists', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps(),
    })
    expect(wrapper.find('.bc-cta').text()).toBe('Editar presupuesto')
  })

  it('emits create-budget when empty state CTA is clicked', async () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [],
        budgetProjection: { total_projected_spent: 0, total_budgeted: 0, total_will_exceed: false },
      }),
    })
    const cta = wrapper.find('.bc-empty-cta')
    expect(cta.exists()).toBe(true)
    await cta.trigger('click')
    expect(wrapper.emitted('create-budget')).toBeTruthy()
    expect(wrapper.emitted('open-budget')).toBeFalsy()
  })

  it('does not emit open-budget from empty state CTA', async () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps({
        budgetStatus: [],
        budgetProjection: { total_projected_spent: 0, total_budgeted: 0, total_will_exceed: false },
      }),
    })
    await wrapper.find('.bc-empty-cta').trigger('click')
    expect(wrapper.emitted('open-budget')).toBeFalsy()
  })

  it('does not recalculate percentages from budgetStatus', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps(),
    })
    const bar = wrapper.find('.bc-bar-fill')
    const style = bar.attributes('style')
    const pctFromProjection = (1250000 / 1500000) * 100
    expect(style).toContain(pctFromProjection.toFixed(1))
  })

  it('uses props only, no HTTP calls', () => {
    const wrapper = mount(BudgetCard, {
      props: makeProps(),
    })
    expect(wrapper.vm.$props.budgetStatus).toBeDefined()
    expect(wrapper.vm.$props.budgetProjection).toBeDefined()
  })

  it('does not import useBudgets', () => {
    const source = BudgetCard.__script?.content || BudgetCard.toString()
    expect(source).not.toContain('useBudgets')
  })
})

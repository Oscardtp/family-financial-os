import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import RecurringCard from '../RecurringCard.vue'

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${Number(v).toLocaleString('es-CO')}`,
    fmtFull: (v) => `$${Number(v).toLocaleString('es-CO')}`,
    fmtDate: (v) => '15 oct 2026',
    fmtMonth: (v) => 'oct 2026',
  }),
}))

function makePayment(overrides = {}) {
  return {
    id: 'rp-001',
    name: 'Netflix',
    amount: 45000,
    type: 'expense',
    frequency: 'monthly',
    next_due_date: '2026-10-15',
    category_id: 'cat-001',
    category_name: 'Entretenimiento',
    ...overrides,
  }
}

function mountCard(props = {}) {
  return mount(RecurringCard, {
    props: { payment: makePayment(), ...props },
    global: { stubs: { teleport: true } },
  })
}

describe('RecurringCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders payment name', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Netflix')
  })

  it('renders formatted amount', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('$45.000')
  })

  it('renders frequency label', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Mensual')
  })

  it('renders next due date', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('oct 2026')
  })

  it('shows registrar pago button', () => {
    const wrapper = mountCard()
    expect(wrapper.find('[data-testid="register-payment-btn"]').exists()).toBe(true)
  })

  it('opens RegisterRecurringPaymentDialog when registrar pago is clicked', async () => {
    const wrapper = mountCard()
    await wrapper.find('[data-testid="register-payment-btn"]').trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.findComponent({ name: 'RegisterRecurringPaymentDialog' }).props('show')).toBe(true)
  })

  it('closes dialog when paid event is emitted', async () => {
    const wrapper = mountCard()
    await wrapper.find('[data-testid="register-payment-btn"]').trigger('click')
    await wrapper.vm.$nextTick()

    const dialog = wrapper.findComponent({ name: 'RegisterRecurringPaymentDialog' })
    await dialog.vm.$emit('paid')
    await wrapper.vm.$nextTick()

    expect(wrapper.findComponent({ name: 'RegisterRecurringPaymentDialog' }).props('show')).toBe(false)
  })

  it('emits refresh after payment', async () => {
    const wrapper = mountCard()
    await wrapper.find('[data-testid="register-payment-btn"]').trigger('click')
    await wrapper.vm.$nextTick()

    const dialog = wrapper.findComponent({ name: 'RegisterRecurringPaymentDialog' })
    await dialog.vm.$emit('paid')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('refresh')).toBeTruthy()
  })

  it('applies expense styling for expense type', () => {
    const wrapper = mountCard({ payment: makePayment({ type: 'expense' }) })
    expect(wrapper.find('.card--expense').exists()).toBe(true)
  })

  it('applies income styling for income type', () => {
    const wrapper = mountCard({ payment: makePayment({ type: 'income' }) })
    expect(wrapper.find('.card--income').exists()).toBe(true)
  })

  it('shows history button', () => {
    const wrapper = mountCard()
    expect(wrapper.find('[data-testid="history-btn"]').exists()).toBe(true)
  })

  it('emits open-history when history button is clicked', async () => {
    const wrapper = mountCard()
    await wrapper.find('[data-testid="history-btn"]').trigger('click')
    expect(wrapper.emitted('open-history')).toBeTruthy()
  })
})

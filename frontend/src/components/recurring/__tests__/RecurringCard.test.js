import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { useRecurringPayments } from '@/composables/useRecurringPayments'

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => ({ path: '/' }),
    useRouter: () => ({ push: vi.fn() }),
  }
})

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({ logout: vi.fn() }),
}))

vi.mock('@/stores/recurringPayments', () => ({
  useRecurringPaymentsStore: () => ({
    items: [],
    loading: { value: false },
    error: { value: null },
    fetchAll: vi.fn(),
    pay: vi.fn(),
    fetchHistory: vi.fn(),
    update: vi.fn(),
    create: vi.fn(),
    remove: vi.fn(),
    toggleActive: vi.fn(),
    fmt: (v) => `$${v}`,
    fmtFull: (v) => `$${v}`,
    fmtDate: (d) => d,
  }),
}))

import RecurringCard from '@/components/recurring/RecurringCard.vue'

function makePayment(overrides = {}) {
  return {
    id: 'rp1',
    name: 'Netflix',
    amount: 45000,
    type: 'expense',
    frequency: 'monthly',
    day_of_month: 15,
    next_due_date: '2026-09-15',
    is_active: true,
    total_paid: 3,
    last_paid_at: '2026-09-10T00:00:00',
    ...overrides,
  }
}

describe('RecurringCard', () => {
  it('renderiza nombre y monto', () => {
    const wrapper = mount(RecurringCard, {
      global: {
        plugins: [createPinia()],
        stubs: {
          RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' },
        },
      },
      props: { payment: makePayment() },
    })
    expect(wrapper.text()).toContain('Netflix')
    expect(wrapper.text()).toContain('$45.000')
  })

  it('muestra frecuencia legible', () => {
    const wrapper = mount(RecurringCard, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
      props: { payment: makePayment({ frequency: 'weekly', day_of_month: 3 }) },
    })
    expect(wrapper.text()).toContain('Cada semana')
  })

  it('muestra el numero de pagos realizados', () => {
    const wrapper = mount(RecurringCard, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
      props: { payment: makePayment({ total_paid: 5 }) },
    })
    expect(wrapper.text()).toContain('Pagado 5 veces')
  })

  it('emite pay al hacer click en pagar', async () => {
    const wrapper = mount(RecurringCard, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
      props: { payment: makePayment() },
    })
    await wrapper.find('.btn-pay').trigger('click')
    expect(wrapper.emitted('pay')).toBeTruthy()
  })

  it('emite history al hacer click en el icono de historial', async () => {
    const wrapper = mount(RecurringCard, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
      props: { payment: makePayment() },
    })
    const buttons = wrapper.findAll('.btn-icon')
    await buttons[1].trigger('click')
    expect(wrapper.emitted('history')).toBeTruthy()
  })

  it('emite edit al hacer click en el icono de editar', async () => {
    const wrapper = mount(RecurringCard, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
      props: { payment: makePayment() },
    })
    const buttons = wrapper.findAll('.btn-icon')
    await buttons[2].trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
  })

  it('no muestra boton de pagar si esta inactivo', () => {
    const wrapper = mount(RecurringCard, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
      props: { payment: makePayment({ is_active: false }) },
    })
    expect(wrapper.find('.btn-pay').exists()).toBe(false)
  })
})

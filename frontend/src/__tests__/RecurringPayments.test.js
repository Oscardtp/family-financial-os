import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { nextTick } from 'vue'

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

vi.mock('@/stores/useCalendar', () => ({
  useCalendarStore: () => ({
    loading: { value: false },
    events: [],
    fetchRange: vi.fn(),
    fetchObligations: vi.fn(),
    fetchAccounts: vi.fn(),
    fetchMembers: vi.fn(),
    openEvent: vi.fn(),
    closeDetail: vi.fn(),
    markPaid: vi.fn(),
    unpayEvent: vi.fn(),
    deleteEvent: vi.fn(),
  }),
}))

vi.mock('@/composables/useAgenda', () => ({
  useAgenda: () => ({
    upcomingEvents: { value: [] },
    availability: { value: null },
    loading: { value: false },
    error: { value: null },
    loadUpcoming: vi.fn(),
    loadAvailability: vi.fn(),
    groupByDate: () => [],
    formatGroupLabel: () => '',
  }),
}))

vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => ({
    notifications: { value: [] },
    unreadCount: { value: 0 },
    loading: { value: false },
    upcoming: { value: { today: [], this_week: [] } },
    upcomingLoading: { value: false },
    upcomingFilter: { value: 'all' },
    filteredUpcoming: { value: [] },
    suggestions: { value: [] },
    suggestionsLoading: { value: false },
    load: vi.fn(),
    loadUpcoming: vi.fn(),
    loadSuggestions: vi.fn(),
    acceptSuggestion: vi.fn(),
    markPaid: vi.fn(),
    markAllRead: vi.fn(),
    markRead: vi.fn(),
    useClickOutside: vi.fn(),
  }),
}))

vi.mock('@/composables/useDashboard', () => ({
  useDashboard: () => ({
    loading: { value: false },
    error: { value: null },
    d: { value: {
      total_balance: 1000000,
      monthly_income: 3000000,
      monthly_expenses: 2000000,
      total_debt: 500000,
      recent_transactions: [],
      savings_summary: { goals: [] },
      fixed_expenses: {
        total_monthly_committed: 125000,
        active_count: 2,
        next_three: [
          { name: 'Netflix', amount: 45000, due_label: 'día 15' },
          { name: 'Spotify', amount: 25000, due_label: 'día 5' },
        ],
        has_insufficient_funds: false,
      },
      upcoming_payments: [],
    }},
    topCategories: { value: [] },
    upcomingPayments: { value: [] },
    monthlyPayments: { value: [] },
    totalMonthlyPaid: { value: 0 },
    totalMonthlyPayment: { value: 100000 },
    totalDebts: { value: 3 },
    paidCount: { value: 1 },
    loadData: vi.fn(),
  }),
}))

vi.mock('@/services/events', () => ({
  eventsService: {
    listRange: vi.fn(),
    get: vi.fn(),
    pay: vi.fn(),
    unpay: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    upcoming: vi.fn(),
    availability: vi.fn(),
    accounts: vi.fn(),
    household: vi.fn(),
  },
  obligationsService: {
    list: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    create: vi.fn(),
  },
}))

vi.mock('@/stores/recurringPayments', () => ({
  useRecurringPaymentsStore: () => ({
    items: [
      { id: 'rp1', name: 'Netflix', amount: 45000, type: 'expense', frequency: 'monthly', day_of_month: 15, next_due_date: '2026-09-15', is_active: true, total_paid: 3, last_paid_at: '2026-09-10' },
      { id: 'rp2', name: 'Spotify', amount: 25000, type: 'expense', frequency: 'monthly', day_of_month: 5, next_due_date: '2026-09-20', is_active: false, total_paid: 1, last_paid_at: null },
    ],
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

vi.mock('@/components/recurring/RecurringCard.vue', () => ({
  default: {
    name: 'RecurringCard',
    template: '<div class="recurring-card-mock"><slot/></div>',
    emits: ['pay', 'history', 'edit', 'toggle-active'],
    props: ['payment'],
  },
}))

vi.mock('@/components/recurring/RecurringHistorySheet.vue', () => ({
  default: {
    name: 'RecurringHistorySheet',
    template: '<div v-if="open" class="history-sheet-mock">sheet</div>',
    props: ['open', 'recurring-id', 'recurring-name'],
    emits: ['close'],
  },
}))

vi.mock('@/components/recurring/RecurringEditModal.vue', () => ({
  default: {
    name: 'RecurringEditModal',
    template: '<div v-if="open" class="edit-modal-mock">modal</div>',
    props: ['open', 'payment'],
    emits: ['close', 'save'],
  },
}))

import RecurringPayments from '@/views/RecurringPayments.vue'

describe('RecurringPayments view', () => {
  it('renderiza la lista de pagos recurrentes', async () => {
    const wrapper = mount(RecurringPayments, {
      global: {
        plugins: [createPinia()],
        stubs: {
          RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' },
        },
      },
    })
    await nextTick()
    const cards = wrapper.findAll('.recurring-card-mock')
    expect(cards.length).toBe(2)
  })

  it('renderiza titulo de pagina', async () => {
    const wrapper = mount(RecurringPayments, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
    })
    await nextTick()
    expect(wrapper.text()).toContain('Pagos recurrentes')
  })

  it('renderiza separador de activos e inactivos', async () => {
    const wrapper = mount(RecurringPayments, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
    })
    await nextTick()
    expect(wrapper.text()).toContain('Activos')
    expect(wrapper.text()).toContain('Inactivos')
  })

  it('renderiza boton para crear pagos recurrentes (FAB)', async () => {
    const wrapper = mount(RecurringPayments, {
      global: {
        plugins: [createPinia()],
        stubs: { RouterLink: { name: 'RouterLink', template: '<a><slot/></a>' } },
      },
    })
    await nextTick()
    expect(wrapper.find('.fab').exists()).toBe(true)
  })
})

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { ref, nextTick } from 'vue'

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

vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => ({
    notifications: ref([]),
    unreadCount: ref(0),
    loading: ref(false),
    upcoming: ref({ today: [], this_week: [] }),
    upcomingLoading: ref(false),
    upcomingFilter: ref('all'),
    filteredUpcoming: ref([]),
    suggestions: ref([]),
    suggestionsLoading: ref(false),
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

vi.mock('@/composables/useAgenda', () => ({
  useAgenda: () => ({
    upcomingEvents: {
      value: [
        { id: '1', title: 'Pago luz', amount: 150000, due_date: '2026-09-12', type: 'expense', status: 'pending' },
        { id: '2', title: 'Salario', amount: 3000000, due_date: '2026-09-13', type: 'income', status: 'pending' },
      ],
    },
    availability: { value: null },
    loading: { value: false },
    error: { value: null },
    loadUpcoming: vi.fn(),
    loadAvailability: vi.fn(),
    groupByDate: (events) => {
      const groups = {}
      for (const ev of events) {
        if (!groups[ev.due_date]) groups[ev.due_date] = { dateStr: ev.due_date, events: [] }
        groups[ev.due_date].events.push(ev)
      }
      return Object.values(groups).sort((a, b) => a.dateStr.localeCompare(b.dateStr))
    },
    formatGroupLabel: (dateStr) => dateStr,
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

import Resumen from '@/views/Resumen.vue'

describe('Resumen', () => {
  it('renderiza seccion Proximos movimientos', async () => {
    const wrapper = mount(Resumen, {
      global: {
        plugins: [createPinia()],
        stubs: {
          RouterLink: {
            name: 'RouterLink',
            template: '<a><slot/></a>',
          },
        },
      },
    })
    await nextTick()
    await nextTick()
    expect(wrapper.text()).toContain('Próximos movimientos')
  })

  it('renderiza link Ver agenda financiera', async () => {
    const wrapper = mount(Resumen, {
      global: {
        plugins: [createPinia()],
        stubs: {
          RouterLink: {
            name: 'RouterLink',
            template: '<a><slot/></a>',
          },
        },
      },
    })
    await nextTick()
    await nextTick()
    expect(wrapper.text()).toContain('Ver agenda financiera')
  })
})

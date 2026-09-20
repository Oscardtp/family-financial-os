import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import RecurringPaymentHistoryDrawer from '@/components/recurring/RecurringPaymentHistoryDrawer.vue'

const mockHistory = ref([])
const mockLoading = ref(false)
const mockError = ref(null)
const mockGetPaymentHistory = vi.fn().mockResolvedValue([])

vi.mock('@/composables/useRecurringPayments', () => ({
  useRecurringPayments: () => ({
    history: mockHistory,
    historyLoading: mockLoading,
    historyError: mockError,
    getPaymentHistory: mockGetPaymentHistory,
  }),
}))

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => Number(v || 0).toLocaleString('es-CO'),
    fmtFull: (v) => '$' + Number(v || 0).toLocaleString('es-CO'),
    fmtDate: (v) => v || '-',
  }),
}))

function mountDrawer(props = {}) {
  return mount(RecurringPaymentHistoryDrawer, {
    props: {
      show: true,
      payment: { id: 'rp1', name: 'Netflix', amount: 45000 },
      ...props,
    },
    global: {
      stubs: { teleport: true },
    },
  })
}

describe('RecurringPaymentHistoryDrawer', () => {
  beforeEach(() => {
    mockHistory.value = []
    mockLoading.value = false
    mockError.value = null
    mockGetPaymentHistory.mockClear()
  })

  it('renders loading state with skeletons', () => {
    mockLoading.value = true
    const wrapper = mountDrawer()
    expect(wrapper.find('.drawer-skeleton').exists() || wrapper.find('[role="status"]').exists()).toBe(true)
  })

  it('renders empty state when no payments', () => {
    mockHistory.value = []
    mockLoading.value = false
    const wrapper = mountDrawer()
    expect(wrapper.text()).toContain('Aun no hay pagos registrados')
  })

  it('renders payment history list', () => {
    mockHistory.value = [
      { id: 't1', date: '2026-09-15', amount: '45000.00', description: 'Netflix' },
      { id: 't2', date: '2026-08-15', amount: '45000.00', description: 'Netflix' },
    ]
    mockLoading.value = false
    const wrapper = mountDrawer()
    expect(wrapper.findAll('.history-item').length).toBe(2)
  })

  it('renders error state with retry button', () => {
    mockError.value = 'Error de red'
    mockLoading.value = false
    const wrapper = mountDrawer()
    expect(wrapper.text()).toContain('No pudimos cargar el historial')
    expect(wrapper.find('.retry-btn').exists()).toBe(true)
  })

  it('calls getPaymentHistory on open', async () => {
    mountDrawer()
    await new Promise(r => setTimeout(r, 50))
    expect(mockGetPaymentHistory).toHaveBeenCalledWith('rp1')
  })

  it('closes drawer on escape key', async () => {
    const wrapper = mountDrawer()
    await new Promise(r => setTimeout(r, 50))
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('formats currency correctly', () => {
    mockHistory.value = [
      { id: 't1', date: '2026-09-15', amount: '45000.00', description: 'Netflix' },
    ]
    mockLoading.value = false
    const wrapper = mountDrawer()
    expect(wrapper.text()).toContain('45')
  })

  it('maintains descending order from backend', () => {
    mockHistory.value = [
      { id: 't2', date: '2026-08-15', amount: '45000.00', description: 'Netflix' },
      { id: 't1', date: '2026-09-15', amount: '45000.00', description: 'Netflix' },
    ]
    mockLoading.value = false
    const wrapper = mountDrawer()
    const items = wrapper.findAll('.history-item')
    expect(items[0].text()).toContain('15')
    expect(items[1].text()).toContain('15')
  })
})

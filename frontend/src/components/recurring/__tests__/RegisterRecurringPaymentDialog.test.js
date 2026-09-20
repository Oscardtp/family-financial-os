import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import RegisterRecurringPaymentDialog from '../RegisterRecurringPaymentDialog.vue'

const mockExecute = vi.fn()
const mockGetPendingEvent = vi.fn()

vi.mock('@/composables/useRecurringPayments', () => ({
  useRecurringPayments: () => ({
    executeRecurringPayment: mockExecute,
    getPendingEvent: mockGetPendingEvent,
  }),
}))

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${Number(v).toLocaleString('es-CO')}`,
    fmtFull: (v) => `$${Number(v).toLocaleString('es-CO')}`,
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
    ...overrides,
  }
}

function mountDialog(props = {}) {
  return mount(RegisterRecurringPaymentDialog, {
    props: { show: true, payment: makePayment(), ...props },
    global: { stubs: { teleport: true } },
  })
}

describe('RegisterRecurringPaymentDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders payment name and amount when show=true', () => {
    const wrapper = mountDialog()
    expect(wrapper.text()).toContain('Netflix')
    expect(wrapper.text()).toContain('$45.000')
  })

  it('does not render when show=false', () => {
    const wrapper = mountDialog({ show: false })
    expect(wrapper.find('.modal-overlay').exists()).toBe(false)
  })

  it('emits close when cancel button is clicked', async () => {
    const wrapper = mountDialog()
    await wrapper.find('[data-testid="cancel-btn"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('emits close and calls execute on confirm', async () => {
    mockGetPendingEvent.mockResolvedValue({ id: 'evt-001' })
    mockExecute.mockResolvedValue({})

    const wrapper = mountDialog()
    await wrapper.find('[data-testid="confirm-btn"]').trigger('click')

    expect(mockGetPendingEvent).toHaveBeenCalledWith('rp-001')
    expect(mockExecute).toHaveBeenCalledWith('evt-001')
    expect(wrapper.emitted('close')).toBeTruthy()
    expect(wrapper.emitted('paid')).toBeTruthy()
  })

  it('shows loading state during execution', async () => {
    let resolvePromise
    mockGetPendingEvent.mockResolvedValue({ id: 'evt-001' })
    mockExecute.mockImplementation(() => new Promise((r) => { resolvePromise = r }))

    const wrapper = mountDialog()
    await wrapper.find('[data-testid="confirm-btn"]').trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-testid="confirm-btn"]').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Registrando')

    resolvePromise()
  })

  it('shows error message on failure', async () => {
    mockGetPendingEvent.mockResolvedValue({ id: 'evt-001' })
    mockExecute.mockRejectedValue({ response: { data: { detail: 'Saldo insuficiente' } } })

    const wrapper = mountDialog()
    await wrapper.find('[data-testid="confirm-btn"]').trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('Saldo insuficiente')
  })

  it('does not call execute if no pending event found', async () => {
    mockGetPendingEvent.mockResolvedValue(null)

    const wrapper = mountDialog()
    await wrapper.find('[data-testid="confirm-btn"]').trigger('click')

    expect(mockExecute).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('No hay evento pendiente')
  })

  it('emits close on escape key', async () => {
    const wrapper = mountDialog()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})

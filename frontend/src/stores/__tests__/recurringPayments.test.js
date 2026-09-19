import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRecurringPaymentsStore } from '../recurringPayments'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({
    fmt: (v) => `$${v}`,
    fmtFull: (v) => `$${v} COP`,
    fmtDate: (d) => d,
    fmtMonth: (d) => d,
  }),
}))

import api from '@/services/api'

function makeRecurring(overrides = {}) {
  return {
    id: 'rp1',
    household_id: 'h1',
    account_id: 'acc1',
    name: 'Netflix',
    amount: 45000,
    type: 'expense',
    frequency: 'monthly',
    day_of_month: 15,
    next_due_date: '2026-09-15',
    is_active: true,
    last_paid_at: null,
    total_paid: 0,
    description: null,
    created_at: '2026-01-01T00:00:00',
    ...overrides,
  }
}

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('useRecurringPaymentsStore', () => {
  it('fetchAll loads items from API', async () => {
    api.get.mockResolvedValue({ data: [makeRecurring(), makeRecurring({ id: 'rp2' })] })
    const store = useRecurringPaymentsStore()
    await store.fetchAll()
    expect(store.items.length).toBe(2)
    expect(api.get).toHaveBeenCalledWith('/recurring-payments')
  })

  it('pay updates local item with API response', async () => {
    api.get.mockResolvedValue({ data: [makeRecurring()] })
    api.post.mockResolvedValue({ data: makeRecurring({ total_paid: 1, last_paid_at: '2026-09-17' }) })
    const store = useRecurringPaymentsStore()
    await store.fetchAll()
    await store.pay('rp1')
    expect(api.post).toHaveBeenCalledWith('/recurring-payments/rp1/pay')
    expect(store.items[0].total_paid).toBe(1)
  })

  it('fetchHistory loads history for a payment', async () => {
    api.get.mockResolvedValueOnce({ data: [] })
    api.get.mockResolvedValueOnce({
      data: [
        { id: 'tx1', recurring_payment_id: 'rp1', amount: 45000, description: 'Netflix', date: '2026-09-15' },
      ],
    })
    const store = useRecurringPaymentsStore()
    await store.fetchAll()
    await store.fetchHistory('rp1')
    expect(api.get).toHaveBeenCalledWith('/recurring-payments/rp1/payments')
    expect(store.history.length).toBe(1)
    expect(store.selectedId).toBe('rp1')
  })

  it('update sends PUT and updates local item', async () => {
    api.get.mockResolvedValue({ data: [makeRecurring()] })
    api.put.mockResolvedValue({ data: makeRecurring({ name: 'Spotify' }) })
    const store = useRecurringPaymentsStore()
    await store.fetchAll()
    await store.update('rp1', { name: 'Spotify' })
    expect(api.put).toHaveBeenCalledWith('/recurring-payments/rp1', { name: 'Spotify' })
    expect(store.items[0].name).toBe('Spotify')
  })

  it('create adds new item to list', async () => {
    api.get.mockResolvedValue({ data: [] })
    api.post.mockResolvedValue({ data: makeRecurring() })
    const store = useRecurringPaymentsStore()
    await store.create({ name: 'Netflix', amount: 45000, type: 'expense' })
    expect(api.post).toHaveBeenCalledWith('/recurring-payments', { name: 'Netflix', amount: 45000, type: 'expense' })
    expect(store.items.length).toBe(1)
  })

  it('toggleActive inverts is_active and calls update', async () => {
    api.get.mockResolvedValue({ data: [makeRecurring({ is_active: true })] })
    api.put.mockResolvedValue({ data: makeRecurring({ is_active: false }) })
    const store = useRecurringPaymentsStore()
    await store.fetchAll()
    const result = await store.toggleActive('rp1')
    expect(api.put).toHaveBeenCalledWith('/recurring-payments/rp1', { is_active: false })
    expect(result.error).toBeNull()
  })

  it('remove deletes item from list', async () => {
    api.get.mockResolvedValue({ data: [makeRecurring(), makeRecurring({ id: 'rp2' })] })
    api.delete.mockResolvedValue({ status: 204 })
    const store = useRecurringPaymentsStore()
    await store.fetchAll()
    await store.remove('rp1')
    expect(api.delete).toHaveBeenCalledWith('/recurring-payments/rp1')
    expect(store.items.length).toBe(1)
  })

  it('pay returns error on API failure', async () => {
    api.post.mockRejectedValue(new Error('fail'))
    const store = useRecurringPaymentsStore()
    const result = await store.pay('rp1')
    expect(result.error).toBe('No pudimos registrar el pago. Intenta de nuevo.')
  })
})

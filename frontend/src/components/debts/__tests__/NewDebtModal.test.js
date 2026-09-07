import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, computed } from 'vue'
import NewDebtModal from '../NewDebtModal.vue'

const createMock = (initial = 0) => ({
  rawValue: ref(initial),
  displayValue: computed({ get: () => '$ 0', set: () => {} }),
  onInput: vi.fn(),
  onFocus: vi.fn(),
  setInitial: vi.fn(),
  formatNumber: vi.fn(),
})

vi.mock('@/composables/useFormattedNumber', () => ({
  useFormattedNumber: () => createMock(),
}))

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

function mountModal(props = {}) {
  return mount(NewDebtModal, {
    props: { show: true, ...props },
    global: {
      stubs: { teleport: true },
    },
  })
}

describe('NewDebtModal', () => {
  it('submits with creditor and total_amount', async () => {
    const wrapper = mountModal()
    const api = (await import('@/services/api')).default
    const postSpy = vi.spyOn(api, 'post').mockResolvedValueOnce({ data: {} })

    wrapper.vm.createForm.creditor = 'Daviplata'
    wrapper.vm.createForm.interest_rate = 24
    wrapper.vm.createForm.interest_rate_type = 'EA'
    wrapper.vm.createForm.debt_type = 'credit_card'
    wrapper.vm.createForm.due_day = 15
    wrapper.vm.createForm.start_date = '2026-01-01'
    wrapper.vm.createForm.note = 'Pago fijo'

    wrapper.vm.fmtAmount.rawValue.value = 5000000
    wrapper.vm.fmtBalance.rawValue.value = 3000000
    wrapper.vm.fmtMinPay.rawValue.value = 150000

    await wrapper.find('form').trigger('submit.prevent')

    expect(postSpy).toHaveBeenCalledWith('/debts', expect.objectContaining({
      creditor: 'Daviplata',
      total_amount: 5000000,
      current_balance: 3000000,
      minimum_payment: 150000,
      interest_rate: 24,
      interest_rate_type: 'EA',
      debt_type: 'credit_card',
      due_day: 15,
      start_date: '2026-01-01',
      note: 'Pago fijo',
    }))
  })

  it('does not send original_amount or créditor', async () => {
    const wrapper = mountModal()
    const api = (await import('@/services/api')).default
    const postSpy = vi.spyOn(api, 'post').mockResolvedValueOnce({ data: {} })

    wrapper.vm.createForm.creditor = 'Banco'
    wrapper.vm.fmtAmount.rawValue.value = 1000000
    wrapper.vm.fmtBalance.rawValue.value = 1000000
    wrapper.vm.fmtMinPay.rawValue.value = 50000

    await wrapper.find('form').trigger('submit.prevent')

    const payload = postSpy.mock.calls[0][1]
    expect(payload).not.toHaveProperty('original_amount')
    expect(payload).not.toHaveProperty('créditor')
  })
})

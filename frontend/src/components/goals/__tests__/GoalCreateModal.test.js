import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GoalCreateModal from '../GoalCreateModal.vue'

vi.mock('@/composables/useSmartCalculator', () => ({
  useSmartCalculator: () => ({
    calcSmartFields: () => ({ summary: '' }),
  }),
}))

function mountModal(props = {}) {
  return mount(GoalCreateModal, {
    props: {
      show: true,
      ...props,
    },
    global: {
      stubs: {
        teleport: true,
      },
    },
  })
}

describe('GoalCreateModal', () => {
  it('does not render when show is false', () => {
    const wrapper = mountModal({ show: false })
    expect(wrapper.find('.modal-overlay').exists()).toBe(false)
  })

  it('renders form fields when show is true', () => {
    const wrapper = mountModal()
    expect(wrapper.find('#goal-name').exists()).toBe(true)
    expect(wrapper.find('#goal-target').exists()).toBe(true)
    expect(wrapper.find('#goal-type').exists()).toBe(true)
    expect(wrapper.find('#goal-priority').exists()).toBe(true)
  })

  it('renders modal title', () => {
    const wrapper = mountModal()
    expect(wrapper.find('.modal-title').text()).toBe('Nueva meta')
  })

  it('emits close event on cancel', async () => {
    const wrapper = mountModal()
    await wrapper.find('.btn-cancel').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('emits close on overlay click', async () => {
    const wrapper = mountModal()
    await wrapper.find('.modal-overlay').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('does not close when clicking modal content', async () => {
    const wrapper = mountModal()
    await wrapper.find('.modal-content').trigger('click')
    expect(wrapper.emitted('close')).toBeFalsy()
  })

  it('disables submit when name is empty', async () => {
    const wrapper = mountModal()
    const btn = wrapper.find('.btn-confirm')
    expect(btn.attributes('disabled')).toBeDefined()
  })

  it('disables submit when target_amount is empty', async () => {
    const wrapper = mountModal()
    await wrapper.find('#goal-name').setValue('Vacaciones')
    const btn = wrapper.find('.btn-confirm')
    expect(btn.attributes('disabled')).toBeDefined()
  })

  it('enables submit when name and target_amount filled', async () => {
    const wrapper = mountModal()
    await wrapper.find('#goal-name').setValue('Vacaciones')
    await wrapper.find('#goal-target').setValue('5000000')
    const btn = wrapper.find('.btn-confirm')
    expect(btn.attributes('disabled')).toBeUndefined()
  })

  it('emits submit with form data', async () => {
    const wrapper = mountModal()
    await wrapper.find('#goal-name').setValue('Vacaciones')
    await wrapper.find('#goal-target').setValue('5000000')
    await wrapper.find('.btn-confirm').trigger('click')
    expect(wrapper.emitted('submit')).toHaveLength(1)
    const data = wrapper.emitted('submit')[0][0]
    expect(data.name).toBe('Vacaciones')
    expect(data.target_amount).toBe(5000000)
    expect(data.goal_type).toBe('savings')
    expect(data.priority).toBe('medium')
  })

  it('shows submitting state', () => {
    const wrapper = mountModal({ submitting: true })
    const btn = wrapper.find('.btn-confirm')
    expect(btn.text()).toContain('Creando')
    expect(btn.attributes('disabled')).toBeDefined()
  })

  it('changes goal_type to investment', async () => {
    const wrapper = mountModal()
    await wrapper.find('#goal-name').setValue('Fondo')
    await wrapper.find('#goal-target').setValue('10000000')
    await wrapper.find('#goal-type').setValue('investment')
    await wrapper.find('.btn-confirm').trigger('click')
    const data = wrapper.emitted('submit')[0][0]
    expect(data.goal_type).toBe('investment')
  })
})

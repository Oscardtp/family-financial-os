import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'

vi.mock('@/stores/useCalendar', () => {
  const event = {
    id: '1',
    title: 'Tarjeta',
    amount: 320000,
    due_date: '2026-09-12',
    type: 'expense',
    status: 'pending',
    obligation_id: 'ob1',
    recommended_date: '2026-09-10',
  }
  const store = {
    loading: { value: false },
    events: [event],
    year: { value: 2026 },
    month: { value: 9 },
    fetchRange: vi.fn(() => Promise.resolve()),
    fetchObligations: vi.fn(),
    fetchAccounts: vi.fn(),
    fetchMembers: vi.fn(),
    openEvent: vi.fn(),
    closeDetail: vi.fn(),
    detailOpen: { value: false },
  }
  return { useCalendarStore: () => store }
})

vi.mock('@/composables/useCalendarNavigation', () => ({
  useCalendarNavigation: () => ({
    monthLabel: { value: 'Septiembre 2026' },
    prevMonth: vi.fn(),
    nextMonth: vi.fn(),
    goToday: vi.fn(),
  }),
}))

vi.mock('@/composables/useCalendarFilters', () => ({
  useCalendarFilters: () => ({
    filteredCalendarDays: { value: [] },
    activeFilter: { value: 'all' },
  }),
}))

vi.mock('@/composables/useCalendarHelpers', () => ({
  eventColor: (ev) => 'ev-default',
  typeIcon: (type) => () => 'Icon',
  fmtDateShort: (dateStr) => {
    if (!dateStr) return ''
    const d = new Date(dateStr + 'T00:00:00')
    return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' }).toUpperCase()
  },
}))

vi.mock('@/components/calendar/CalendarGridView.vue', () => ({
  __esModule: true,
  default: {
    name: 'CalendarGridView',
    props: [
      'days', 'monthLabel', 'loading', 'selectedDate', 'filter', 'eventColor',
    ],
    emits: ['update:filter', 'selectDay', 'createOnDate', 'prev', 'next', 'today'],
    template: '<div class="calendar-grid-view-mock" />',
  },
}))

import CalendarBottomSheet from '@/components/calendar/CalendarBottomSheet.vue'

describe('CalendarBottomSheet', () => {
  async function openSheet() {
    const wrapper = mount(CalendarBottomSheet, {
      props: { open: false },
      global: { plugins: [createPinia()] },
    })
    await wrapper.setProps({ open: true })
    await new Promise(r => setTimeout(r, 50))
    return wrapper
  }

  it('no renderiza nada cuando open es false', () => {
    const wrapper = mount(CalendarBottomSheet, {
      props: { open: false },
      global: { plugins: [createPinia()] },
    })
    expect(wrapper.find('.cal-sheet').exists()).toBe(false)
  })

  it('renderiza el sheet cuando open es true', async () => {
    const wrapper = await openSheet()
    expect(wrapper.find('.cal-sheet').exists()).toBe(true)
  })

  it('renderiza el handle de arrastre', async () => {
    const wrapper = await openSheet()
    expect(wrapper.find('.cal-sheet-handle').exists()).toBe(true)
  })

  it('no renderiza el botón X de cerrar', async () => {
    const wrapper = await openSheet()
    expect(wrapper.find('.cal-sheet-close').exists()).toBe(false)
  })

  it('no renderiza CalendarEventDetailSheet dentro del bottom sheet', async () => {
    const wrapper = await openSheet()
    expect(wrapper.findComponent({ name: 'CalendarEventDetailSheet' }).exists()).toBe(false)
  })

  it('muestra el detalle inline cuando se selecciona un día con eventos', async () => {
    const wrapper = await openSheet()
    await wrapper.vm.handleSelectDay('2026-09-12')
    expect(wrapper.find('.cal-day-detail').exists()).toBe(true)
    expect(wrapper.text()).toContain('Tarjeta')
    expect(wrapper.text()).toContain('320.000')
  })

  it('no muestra detalle inline cuando el día no tiene eventos', async () => {
    const wrapper = await openSheet()
    await wrapper.vm.handleSelectDay('2026-09-15')
    expect(wrapper.find('.cal-day-detail').exists()).toBe(false)
  })

  it('muestra botón Ver deuda solo si existe obligation_id', async () => {
    const wrapper = await openSheet()
    await wrapper.vm.handleSelectDay('2026-09-12')
    expect(wrapper.find('.cal-day-detail-link').exists()).toBe(true)
    expect(wrapper.text()).toContain('Ver deuda')
  })

  it('emite showObligationInfo al hacer clic en Ver deuda', async () => {
    const wrapper = await openSheet()
    await wrapper.vm.handleSelectDay('2026-09-12')
    await wrapper.find('.cal-day-detail-link').trigger('click')
    expect(wrapper.emitted('showObligationInfo')).toBeTruthy()
    expect(wrapper.emitted('showObligationInfo')[0]).toEqual(['ob1'])
  })

  it('muestra todos los eventos del día en el detalle inline', async () => {
    const wrapper = await openSheet()
    const store = wrapper.vm.store
    store.events = [
      { id: '1', title: 'Tarjeta', amount: 320000, due_date: '2026-09-12', type: 'expense', status: 'pending', obligation_id: 'ob1', recommended_date: '2026-09-10' },
      { id: '2', title: 'Salario', amount: 3800000, due_date: '2026-09-12', type: 'income', status: 'pending' },
    ]
    await wrapper.vm.handleSelectDay('2026-09-12')
    expect(wrapper.find('.cal-day-detail').exists()).toBe(true)
    expect(wrapper.text()).toContain('Tarjeta')
    expect(wrapper.text()).toContain('Salario')
    expect(wrapper.text()).toContain('320.000')
    expect(wrapper.text()).toContain('3.800.000')
    expect(wrapper.findAll('.cal-day-detail-item').length).toBe(2)
  })

  it('permite seleccionar un evento individual en la lista del día', async () => {
    const wrapper = await openSheet()
    const store = wrapper.vm.store
    store.events = [
      { id: '1', title: 'Tarjeta', amount: 320000, due_date: '2026-09-12', type: 'expense', status: 'pending', obligation_id: 'ob1' },
      { id: '2', title: 'Salario', amount: 3800000, due_date: '2026-09-12', type: 'income', status: 'pending' },
    ]
    await wrapper.vm.handleSelectDay('2026-09-12')
    await wrapper.findAll('.cal-day-detail-item').at(1).trigger('click')
    expect(wrapper.emitted('selectEvent').length).toBe(2)
    expect(wrapper.emitted('selectEvent')[1][0]).toEqual(expect.objectContaining({
      id: '2',
      title: 'Salario',
    }))
  })
})

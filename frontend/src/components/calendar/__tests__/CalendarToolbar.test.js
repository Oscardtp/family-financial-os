import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CalendarToolbar from '../CalendarToolbar.vue'

describe('CalendarToolbar', () => {
  it('renderiza mes y botones de navegacion', () => {
    const wrapper = mount(CalendarToolbar, {
      props: {
        monthLabel: 'Septiembre 2026',
      },
    })
    expect(wrapper.text()).toContain('Septiembre 2026')
    expect(wrapper.text()).toContain('Hoy')
  })

  it('emite today al hacer click en Hoy', async () => {
    const wrapper = mount(CalendarToolbar, {
      props: {
        monthLabel: 'Septiembre 2026',
      },
    })
    await wrapper.find('.btn-today').trigger('click')
    expect(wrapper.emitted('today')).toBeTruthy()
  })

  it('emite prev al hacer click en flecha izquierda', async () => {
    const wrapper = mount(CalendarToolbar, {
      props: {
        monthLabel: 'Septiembre 2026',
      },
    })
    await wrapper.find('.btn-icon[aria-label="Mes anterior"]').trigger('click')
    expect(wrapper.emitted('prev')).toBeTruthy()
  })

  it('emite next al hacer click en flecha derecha', async () => {
    const wrapper = mount(CalendarToolbar, {
      props: {
        monthLabel: 'Septiembre 2026',
      },
    })
    await wrapper.find('.btn-icon[aria-label="Mes siguiente"]').trigger('click')
    expect(wrapper.emitted('next')).toBeTruthy()
  })

  it('no renderiza tabs Lista/Calendario', () => {
    const wrapper = mount(CalendarToolbar, {
      props: {
        monthLabel: 'Septiembre 2026',
      },
    })
    expect(wrapper.text()).not.toContain('Lista')
    expect(wrapper.text()).not.toContain('Calendario')
  })
})

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CalendarToolbar from '../CalendarToolbar.vue'

describe('CalendarToolbar', () => {
  it('does not render Admin recurrentes button', () => {
    const wrapper = mount(CalendarToolbar, {
      props: {
        viewMode: 'calendar',
        activeFilter: 'all',
        monthLabel: 'Enero 2025',
        filters: [
          { key: 'all', label: 'Todos' },
          { key: 'paid', label: 'Pagados' },
        ],
      },
    })
    expect(wrapper.text()).not.toContain('Admin recurrentes')
  })
})
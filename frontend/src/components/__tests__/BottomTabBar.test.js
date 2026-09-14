import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BottomTabBar from '../BottomTabBar.vue'

describe('BottomTabBar', () => {
  it('has 4 tabs without Calendario', () => {
    const wrapper = mount(BottomTabBar, {
      global: {
        stubs: {
          RouterLink: {
            name: 'RouterLink',
            template: '<a><slot/></a>',
          },
        },
        mocks: {
          $route: { path: '/' },
        },
      },
    })
    expect(wrapper.text()).not.toContain('Calendario')
    expect(wrapper.findAll('.tab-item').length).toBe(4)
  })
})

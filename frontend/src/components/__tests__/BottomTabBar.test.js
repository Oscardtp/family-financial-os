import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { useRoute } from 'vue-router'

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => ({ path: '/' }),
  }
})

import BottomTabBar from '../BottomTabBar.vue'

describe('BottomTabBar', () => {
  it('shows Calendario label for calendar tab', () => {
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
    expect(wrapper.text()).toContain('Calendario')
    expect(wrapper.text()).not.toContain(' Pagos ')
  })
})

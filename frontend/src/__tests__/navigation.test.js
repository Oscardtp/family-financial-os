import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => ({ path: '/' }),
    useRouter: () => ({ push: vi.fn() }),
  }
})

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({ logout: vi.fn() }),
}))

import AppLayout from '@/components/AppLayout.vue'
import BottomTabBar from '@/components/BottomTabBar.vue'
import router from '@/router'

describe('Navigation', () => {
  it('sidebar does not contain Calendario item', () => {
    const wrapper = mount(AppLayout, {
      global: {
        plugins: [createPinia()],
        mocks: {
          $route: { path: '/' },
        },
        stubs: {
          RouterLink: {
            name: 'RouterLink',
            template: '<a><slot/></a>',
          },
        },
      },
    })
    expect(wrapper.text()).not.toContain('Calendario')
  })

  it('bottom tab bar has 4 tabs without Calendario', () => {
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
    const tabs = wrapper.findAll('.tab-item')
    expect(tabs.length).toBe(4)
    expect(wrapper.text()).not.toContain('Calendario')
  })

  it('router has no Calendar named route', () => {
    expect(router.hasRoute('Calendar')).toBe(false)
  })

  it('router has no AgendaFinanciera named route', () => {
    expect(router.hasRoute('AgendaFinanciera')).toBe(false)
  })
})

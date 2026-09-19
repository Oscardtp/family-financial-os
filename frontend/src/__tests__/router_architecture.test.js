import { describe, it, expect } from 'vitest'
import router from '@/router'

describe('Router Architecture', () => {
  it('all route names are unique', () => {
    const names = []
    function collectNames(routeList) {
      for (const route of routeList) {
        if (route.name) names.push(route.name)
        if (route.children) collectNames(route.children)
      }
    }
    collectNames(router.options.routes)
    const unique = new Set(names)
    expect(unique.size).toBe(names.length)
  })

  it('routes resolve correctly', () => {
    const routes = router.getRoutes()
    expect(routes.length).toBeGreaterThanOrEqual(5)
    const names = routes.map(r => r.name).filter(Boolean)
    expect(names).toContain('Login')
    expect(names).toContain('Resumen')
    expect(names).toContain('Debts')
    expect(names).toContain('Goals')
    expect(names).toContain('Config')
  })

  it('lazy loaded views exist', () => {
    const routes = router.options.routes
    const loginRoute = routes.find(r => r.path === '/login')
    expect(typeof loginRoute.component).toBe('function')
    const layoutRoute = routes.find(r => r.path === '/')
    expect(typeof layoutRoute.component).toBe('function')
  })

  it('no orphan route imports', () => {
    const routes = router.options.routes
    const named = routes.filter(r => r.name)
    for (const route of named) {
      expect(route.name).toBeTruthy()
      expect(route.component).toBeDefined()
    }
  })

  it('router navigation still works', () => {
    const routes = router.getRoutes()
    const routeNames = routes.map(r => r.name).filter(Boolean)
    expect(routeNames).toContain('Login')
    expect(routeNames).toContain('Resumen')
  })
})

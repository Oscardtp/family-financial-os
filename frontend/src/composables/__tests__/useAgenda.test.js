import { describe, it, expect } from 'vitest'
import { useAgenda } from '@/composables/useAgenda'

describe('useAgenda', () => {
  it('groupByDate agrupa eventos por fecha', () => {
    const events = [
      { id: 1, due_date: '2026-09-12', title: 'Pago 1', amount: 100 },
      { id: 2, due_date: '2026-09-12', title: 'Pago 2', amount: 200 },
      { id: 3, due_date: '2026-09-13', title: 'Ingreso 1', amount: 500 },
    ]
    const grouped = useAgenda().groupByDate(events)
    expect(grouped).toHaveLength(2)
    expect(grouped[0].dateStr).toBe('2026-09-12')
    expect(grouped[0].events).toHaveLength(2)
    expect(grouped[1].dateStr).toBe('2026-09-13')
    expect(grouped[1].events).toHaveLength(1)
  })

  it('formatGroupLabel retorna HOY para fecha actual', () => {
    const today = new Date().toISOString().slice(0, 10)
    expect(useAgenda().formatGroupLabel(today)).toBe('HOY')
  })

  it('formatGroupLabel retorna MAÑANA para fecha siguiente', () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowStr = tomorrow.toISOString().slice(0, 10)
    expect(useAgenda().formatGroupLabel(tomorrowStr)).toBe('MAÑANA')
  })

  it('formatGroupLabel retorna fecha formateada para fechas lejanas', () => {
    const future = new Date()
    future.setDate(future.getDate() + 10)
    const futureStr = future.toISOString().slice(0, 10)
    const label = useAgenda().formatGroupLabel(futureStr)
    expect(label).not.toBe('HOY')
    expect(label).not.toBe('MAÑANA')
    expect(label.length).toBeGreaterThan(0)
  })
})

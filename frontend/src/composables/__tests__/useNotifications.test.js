import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotifications } from '@/composables/useNotifications'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

vi.mock('@/services/events', () => ({
  eventsService: {
    pay: vi.fn(),
  },
}))

import api from '@/services/api'
import { eventsService } from '@/services/events'

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
})

describe('useNotifications', () => {
  describe('inbox', () => {
    it('loads notifications and unread count', async () => {
      const notifications = [{ id: 'n1', title: 'Hola' }]
      api.get.mockResolvedValueOnce({ data: notifications }).mockResolvedValueOnce({ data: { count: 1 } })
      const { load, notifications: n, unreadCount } = useNotifications()
      await load()
      expect(n.value).toEqual(notifications)
      expect(unreadCount.value).toBe(1)
    })

    it('marks all as read', async () => {
      api.post.mockResolvedValue({})
      const { markAllRead, notifications, unreadCount } = useNotifications()
      notifications.value = [
        { id: 'n1', is_read: false },
        { id: 'n2', is_read: false },
      ]
      await markAllRead()
      expect(notifications.value.every(n => n.is_read)).toBe(true)
      expect(unreadCount.value).toBe(0)
    })
  })

  describe('upcoming', () => {
    it('loads upcoming notifications', async () => {
      api.get.mockResolvedValue({ data: { today: [], this_week: [] } })
      const { loadUpcoming, upcoming } = useNotifications()
      await loadUpcoming(7)
      expect(upcoming.value.today).toEqual([])
      expect(upcoming.value.this_week).toEqual([])
      expect(api.get).toHaveBeenCalledWith('/notifications/upcoming', { params: { days: 7 } })
    })

    it('filters upcoming by filter type', async () => {
      const { upcoming, upcomingFilter, filteredUpcoming } = useNotifications()
      upcoming.value = {
        today: [{ event_id: 'e1', title: 'Hoy', amount: 1000, due_date: '2026-08-27', level: 'Hoy' }],
        this_week: [{ event_id: 'e2', title: 'Mañana', amount: 2000, due_date: '2026-08-28', level: 'Mañana' }],
      }
      upcomingFilter.value = 'all'
      expect(filteredUpcoming()).toHaveLength(2)

      upcomingFilter.value = 'today'
      expect(filteredUpcoming()).toHaveLength(1)
      expect(filteredUpcoming()[0].title).toBe('Hoy')
    })

    it('marks an upcoming event as paid', async () => {
      api.post.mockResolvedValue({})
      const { markPaid, upcoming } = useNotifications()
      upcoming.value = {
        today: [{ event_id: 'e1', title: 'Hoy', amount: 1000, due_date: '2026-08-27', level: 'Hoy' }],
        this_week: [],
      }
      eventsService.pay.mockResolvedValue({})
      await markPaid('e1')
      expect(eventsService.pay).toHaveBeenCalledWith('e1')
    })
  })
})

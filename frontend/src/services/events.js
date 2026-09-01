  import api from '@/services/api'
  
  export const coachService = {
    suggestions: () => api.get('/coach/suggestions'),
    patterns: () => api.get('/coach/patterns'),
    accept: (data) => api.post('/obligations', data),
  }
  
  export const eventsService = {
    listMonth: (year, month) => api.get('/events', { params: { year, month } }),
    listRange: (from, to) => api.get('/events', { params: { from_date: from, to_date: to } }),
    upcoming: (days = 30) => api.get('/events/upcoming', { params: { days } }),
    availability: (days = 7) => api.get('/events/availability', { params: { days } }),
    get: (id) => api.get(`/events/${id}`),
    create: (data) => api.post('/events', data),
    update: (id, data) => api.put(`/events/${id}`, data),
    remove: (id) => api.delete(`/events/${id}`),
    pay: (id) => api.post(`/events/${id}/pay`),
    unpay: (id) => api.post(`/events/${id}/unpay`),
    accounts: () => api.get('/accounts'),
    household: () => api.get('/household'),
    prepareMonth: () => api.get('/month/prepare'),
    createObligationFromEvent: (data) => api.post('/obligations/from-event', data),
  }

  export const obligationsService = {
    list: () => api.get('/obligations'),
    create: (data) => api.post('/obligations', data),
    get: (id) => api.get(`/obligations/${id}`),
    update: (id, data) => api.put(`/obligations/${id}`, data),
    remove: (id) => api.delete(`/obligations/${id}`),
  }

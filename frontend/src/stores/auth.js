import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function register(email, name, password) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post('/auth/register', { email, name, password })
      token.value = data.access_token
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchUser()
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || 'No pudimos crear tu cuenta. Intenta de nuevo.'
      return false
    } finally {
      loading.value = false
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.post('/auth/login', { email, password })
      token.value = data.access_token
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchUser()
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || 'No pudimos iniciar sesión. Intenta de nuevo.'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await api.get('/auth/me')
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, token, loading, error, isAuthenticated, register, login, fetchUser, logout }
})

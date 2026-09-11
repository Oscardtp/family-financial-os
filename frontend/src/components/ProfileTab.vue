<template>
  <div class="profile-tab">
    <div class="config-section card profile-card">
      <div class="profile-avatar">{{ userInitials }}</div>
      <div class="profile-details">
        <h3 class="profile-name">{{ user?.name || 'Sin nombre' }}</h3>
        <span class="profile-email">{{ user?.email || 'Sin email' }}</span>
      </div>
    </div>

    <div class="config-section card">
      <h3 class="section-title">Datos</h3>
      <div class="config-row">
        <span class="config-label">Exportar movimientos</span>
        <button class="btn btn-sm btn-outline" @click="exportCSV" :disabled="exporting">
          {{ exporting ? 'Descargando...' : 'Descargar CSV' }}
        </button>
      </div>
    </div>

    <div class="config-section card">
      <h3 class="section-title">Sesión</h3>
      <button class="btn btn-sm btn-danger" @click="handleLogout">Cerrar sesión</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()
const user = computed(() => auth.user)

const userInitials = computed(() => {
  const name = auth.user?.name || ''
  const parts = name.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.slice(0, 2).toUpperCase()
})

const exporting = ref(false)

async function exportCSV() {
  exporting.value = true
  try {
    const response = await api.get('/reports/transactions/csv', { responseType: 'blob' })
    const text = await response.data.text()
    if (!text || text.trim().length < 10) {
      toast.info('No hay datos para descargar en este momento.')
      return
    }
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'movimientos.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    toast.success('Descarga completada')
  } catch {
    toast.error('No pudimos descargar. Intenta de nuevo.')
  } finally {
    exporting.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.config-section { margin-bottom: var(--spacing-md); }
.config-row { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-100); }
.config-row:last-child { border-bottom: none; }
.config-label { font-size: 0.875rem; color: var(--color-neutral-600); }

.profile-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
}
.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  background: var(--color-primary-600);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 1.25rem;
  flex-shrink: 0;
}
.profile-details { display: flex; flex-direction: column; gap: 2px; }
.profile-name { font-size: 1.1rem; font-weight: 600; color: var(--color-neutral-900); margin: 0; }
.profile-email { font-size: 0.85rem; color: var(--color-neutral-500); }
</style>

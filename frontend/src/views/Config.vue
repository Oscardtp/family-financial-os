<template>
  <div class="config-page">
    <h2 class="page-title">Configuracion</h2>

    <div class="config-section card">
      <h3 class="section-title">Tu perfil</h3>
      <div class="config-row">
        <span class="config-label">Nombre</span>
        <span class="config-value">{{ user?.name || 'Sin nombre' }}</span>
      </div>
      <div class="config-row">
        <span class="config-label">Email</span>
        <span class="config-value">{{ user?.email || 'Sin email' }}</span>
      </div>
    </div>

    <div class="config-section card">
      <h3 class="section-title">Hogar</h3>
      <div class="config-row">
        <span class="config-label">Tu familia</span>
        <router-link to="/household" class="config-link">Ver miembros →</router-link>
      </div>
      <div class="config-row">
        <span class="config-label">Categorias</span>
        <router-link to="/categories" class="config-link">Administrar →</router-link>
      </div>
    </div>

    <div class="config-section card">
      <h3 class="section-title">Datos</h3>
      <div class="config-row">
        <span class="config-label">Exportar movimientos</span>
        <button class="btn btn-sm btn-outline" @click="exportCSV">Descargar CSV</button>
      </div>
    </div>

    <div class="config-section card">
      <h3 class="section-title">Sesion</h3>
      <button class="btn btn-sm btn-danger" @click="handleLogout">Cerrar sesion</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()
const user = computed(() => auth.user)

async function exportCSV() {
  try {
    const response = await api.get('/reports/transactions/csv', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'movimientos.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (e) {
    console.error('Error exporting CSV:', e)
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.config-page {
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-neutral-900);
  margin-bottom: var(--space-xl);
}

.config-section {
  margin-bottom: var(--space-md);
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-neutral-700);
  margin-bottom: var(--space-md);
}

.config-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--color-neutral-100);
}

.config-row:last-child {
  border-bottom: none;
}

.config-label {
  font-size: 0.875rem;
  color: var(--color-neutral-600);
}

.config-value {
  font-size: 0.875rem;
  color: var(--color-neutral-900);
  font-weight: 500;
}

.config-link {
  font-size: 0.85rem;
  color: var(--color-primary-600);
  text-decoration: none;
  font-weight: 500;
}

.config-link:hover {
  text-decoration: underline;
}

.btn-sm {
  font-size: 0.8rem;
  padding: var(--space-xs) var(--space-md);
}

.btn-outline {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  color: var(--color-neutral-700);
}

.btn-outline:hover {
  border-color: var(--color-primary-400);
  color: var(--color-primary-600);
}

.btn-danger {
  background: var(--color-error-600);
  color: white;
}

.btn-danger:hover {
  background: var(--color-error-700);
}
</style>

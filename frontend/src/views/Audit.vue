<template>
  <div class="audit-page">
    <div class="page-header">
      <h2 class="page-title">
        Registro de Auditoria
      </h2>
    </div>

    <div
      v-if="loading"
      class="loading-state"
    >
      <div class="spinner" />
      <span>Cargando registros...</span>
    </div>

    <div
      v-else-if="error"
      class="error-state"
    >
      <span>{{ error }}</span>
      <button
        class="btn btn-sm"
        @click="loadLogs"
      >
        Reintentar
      </button>
    </div>

    <template v-else>
      <div class="card">
        <div
          v-if="logs.length"
          class="log-list"
        >
          <div
            v-for="log in logs"
            :key="log.id"
            class="log-item"
          >
            <div class="log-info">
              <span class="log-date">{{ formatDate(log.created_at) }}</span>
              <span class="log-user">{{ log.user_email || 'Sistema' }}</span>
            </div>
            <div class="log-detail">
              <span
                class="log-action"
                :class="'action-' + log.action"
              >
                {{ actionLabel(log.action) }}
              </span>
              <span class="log-entity">{{ log.entity_type }}</span>
              <span
                v-if="log.entity_name"
                class="log-entity-name"
              >{{ log.entity_name }}</span>
            </div>
          </div>
        </div>
        <p
          v-else
          class="empty-text"
        >
          No hay registros de auditoría todavía
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const logs = ref([])
const loading = ref(true)
const error = ref('')

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' })
}

function actionLabel(action) {
  const map = { create: 'Creo', update: 'Actualizo', delete: 'Elimino' }
  return map[action] || action
}

async function loadLogs() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/audit')
    logs.value = data
  } catch (e) {
    error.value = 'Error al cargar los registros'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadLogs)
</script>

<style scoped>
.audit-page { max-width: 960px; margin: 0 auto; }
.page-header { margin-bottom: var(--spacing-xl); }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.log-list { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.log-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-neutral-100);
}
.log-item:last-child { border-bottom: none; }
.log-info { display: flex; flex-direction: column; gap: 2px; }
.log-date { font-size: 0.8rem; color: var(--color-neutral-400); }
.log-user { font-size: 0.875rem; color: var(--color-neutral-600); }
.log-detail { display: flex; align-items: center; gap: var(--spacing-sm); }
.log-action {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}
.action-create { background: var(--color-success-100); color: var(--color-success-700); }
.action-update { background: var(--color-primary-100); color: var(--color-primary-700); }
.action-delete { background: var(--color-error-100); color: var(--color-error-700); }
.log-entity { font-size: 0.8rem; color: var(--color-neutral-500); }
.log-entity-name { font-size: 0.8rem; font-weight: 600; color: var(--color-neutral-700); }
.empty-text { color: var(--color-neutral-400); font-size: 0.875rem; text-align: center; padding: var(--spacing-lg); }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }

@media (max-width: 640px) {
  .audit-page {
    padding: 0;
  }
  .log-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
    background: var(--color-neutral-0);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-neutral-200);
  }
  .log-detail {
    flex-wrap: wrap;
    gap: var(--spacing-xs);
  }
}
</style>

<template>
  <div v-if="error" class="error-boundary" role="alert">
    <div class="error-content">
      <AlertTriangle :size="48" class="error-icon" />
      <h2 class="error-title">Ups, algo falló</h2>
      <p class="error-message">{{ error.message || 'No esperábamos esto. ¿Recargas la página?' }}</p>
      <div class="error-actions">
        <button class="btn-retry" @click="retry">
          <RefreshCw :size="16" />
          Reintentar
        </button>
        <button class="btn-home" @click="goHome">
          <Home :size="16" />
          Ir al inicio
        </button>
      </div>
      <details class="error-details">
        <summary>Más información</summary>
        <pre>{{ error.stack || error.message }}</pre>
      </details>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, RefreshCw, Home } from 'lucide-vue-next'

const router = useRouter()
const error = ref(null)

onErrorCaptured((err) => {
  error.value = err
  return false
})

function retry() {
  error.value = null
  window.location.reload()
}

function goHome() {
  error.value = null
  router.push('/')
}
</script>

<style scoped>
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 32px;
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  color: #d97706;
  margin-bottom: 16px;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.error-message {
  color: #6b7280;
  margin-bottom: 24px;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.btn-retry,
.btn-home {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
}

.btn-retry {
  background: #2563eb;
  color: white;
}

.btn-retry:hover {
  background: #1d4ed8;
}

.btn-home {
  background: #f3f4f6;
  color: #374151;
}

.btn-home:hover {
  background: #e5e7eb;
}

.error-details {
  text-align: left;
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
}

.error-details summary {
  cursor: pointer;
  font-size: 0.875rem;
  color: #6b7280;
}

.error-details pre {
  margin-top: 8px;
  font-size: 0.75rem;
  color: #dc2626;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>

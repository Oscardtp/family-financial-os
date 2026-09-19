<template>
  <transition name="slide-up">
    <div
      v-if="open"
      class="sheet-backdrop"
      @click.self="handleClose"
    >
      <div class="sheet-content" role="dialog" aria-modal="true" aria-label="Historial de pagos">
        <div class="sheet-handle" />
        <div class="sheet-header">
          <h3 class="sheet-title">Historial de pagos</h3>
          <button class="btn-icon" @click="handleClose" aria-label="Cerrar" :title="recurringName">
            <X :size="20" />
          </button>
        </div>

        <div v-if="loading" class="sheet-loading">
          <div class="spinner-large" />
        </div>

        <div v-else-if="!loading && payments.length === 0" class="sheet-empty">
          <History :size="32" class="empty-icon" />
          <p class="empty-text">Aún no hay pagos registrados</p>
        </div>

        <div v-else class="sheet-list">
          <div
            v-for="tx in payments"
            :key="tx.id"
            class="sheet-item"
          >
            <div class="sheet-item-info">
              <span class="sheet-item-desc">{{ tx.description || 'Pago' }}</span>
              <span class="sheet-item-date">{{ formatDate(tx.date) }}</span>
            </div>
            <span class="sheet-item-amount" :class="tx.type">
              {{ tx.type === 'income' ? '+' : '-' }}{{ fmtFull(tx.amount) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { X, History } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import { useRecurringPaymentsStore } from '@/stores/recurringPayments'

const props = defineProps({
  open: { type: Boolean, default: false },
  recurringId: { type: String, default: null },
  recurringName: { type: String, default: 'este pago' },
})

const emit = defineEmits(['close'])

const { fmtFull } = useCurrency()
const store = useRecurringPaymentsStore()
const loading = ref(false)
const payments = ref([])

async function loadHistory() {
  if (!props.recurringId) return
  loading.value = true
  try {
    await store.fetchHistory(props.recurringId)
    payments.value = store.history || []
  } finally {
    loading.value = false
  }
}

function handleClose() {
  emit('close')
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' })
}

watch(
  () => props.open,
  (val) => {
    if (val) loadHistory()
  }
)

onMounted(() => {
  if (props.open && props.recurringId) loadHistory()
})
</script>

<style scoped>
.sheet-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 200;
}
.sheet-content {
  background: var(--color-neutral-0);
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 640px;
  margin: auto;
  padding: 12px 20px 20px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
[data-theme="dark"] .sheet-content {
  background: var(--color-neutral-900);
}
.sheet-handle {
  width: 40px;
  height: 4px;
  background: var(--color-neutral-300);
  border-radius: 2px;
  margin: 0 auto 12px;
}
.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.sheet-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin: 0;
}
.sheet-loading {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 32px 0;
}
.sheet-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  padding: 32px 0;
}
.empty-icon {
  color: var(--color-neutral-300);
}
.empty-text {
  color: var(--color-neutral-500);
  font-size: 0.9rem;
}
.sheet-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 8px;
}
.sheet-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-neutral-100);
}
.sheet-item:last-child {
  border-bottom: none;
}
.sheet-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sheet-item-desc {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-neutral-800);
}
.sheet-item-date {
  font-size: 0.75rem;
  color: var(--color-neutral-500);
}
.sheet-item-amount {
  font-size: 0.95rem;
  font-weight: 600;
  font-family: var(--font-mono);
}
.sheet-item-amount.income { color: var(--color-success-600); }
.sheet-item-amount.expense { color: var(--color-error-600); }
.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-neutral-600);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-icon:hover {
  background: var(--color-neutral-100);
}
.spinner-large {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.slide-up-enter-active, .slide-up-leave-active { transition: opacity 200ms, transform 200ms; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(20px); }
</style>

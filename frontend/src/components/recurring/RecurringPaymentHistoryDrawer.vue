<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="show" class="drawer-overlay" @click.self="$emit('close')">
        <div class="drawer-panel" @click.stop>
          <div class="drawer-header">
            <div class="drawer-header-info">
              <h3 class="drawer-title">{{ payment?.name }}</h3>
              <span class="drawer-amount">{{ fmtFull(payment?.amount) }}</span>
            </div>
            <button class="drawer-close" @click="$emit('close')" aria-label="Cerrar">
              <X :size="20" />
            </button>
          </div>

          <div class="drawer-body">
            <div v-if="historyLoading" class="drawer-skeleton">
              <div v-for="n in 3" :key="n" class="skeleton-row">
                <SkeletonLoader variant="text" width="100px" />
                <SkeletonLoader variant="text" width="80px" />
              </div>
            </div>

            <div v-else-if="historyError" class="drawer-error">
              <AlertCircle :size="24" />
              <p>No pudimos cargar el historial</p>
              <button class="retry-btn" @click="retry">Intentar de nuevo</button>
            </div>

            <div v-else-if="history.length === 0" class="drawer-empty">
              <Receipt :size="28" />
              <p>Aun no hay pagos registrados</p>
              <span class="drawer-empty-hint">El historial aparecera cuando este pago se procese por primera vez.</span>
            </div>

            <template v-else>
              <div class="drawer-summary">
                <span>{{ history.length }} {{ history.length === 1 ? 'pago' : 'pagos' }}</span>
              </div>

              <div class="drawer-list">
                <div
                  v-for="item in history"
                  :key="item.id"
                  class="history-item"
                >
                  <div class="history-left">
                    <span class="history-date">{{ fmtDate(item.date) }}</span>
                    <span class="history-desc">{{ item.description }}</span>
                  </div>
                  <div class="history-right">
                    <span class="history-amount">{{ fmtFull(item.amount) }}</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch, onMounted, onUnmounted } from 'vue'
import { X, AlertCircle, Receipt } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import { useRecurringPayments } from '@/composables/useRecurringPayments'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { fmtFull, fmtDate } = useCurrency()
const { history, historyLoading, historyError, getPaymentHistory } = useRecurringPayments()

const props = defineProps({
  show: { type: Boolean, default: false },
  payment: { type: Object, default: null },
})

const emit = defineEmits(['close'])

function handleKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

function retry() {
  if (props.payment?.id) {
    getPaymentHistory(props.payment.id)
  }
}

watch(() => props.show, (val) => {
  if (val && props.payment?.id) {
    getPaymentHistory(props.payment.id)
    document.addEventListener('keydown', handleKeydown)
  } else {
    document.removeEventListener('keydown', handleKeydown)
  }
})

onMounted(() => {
  if (props.show && props.payment?.id) {
    getPaymentHistory(props.payment.id)
    document.addEventListener('keydown', handleKeydown)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: var(--z-modal);
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: 380px;
  max-width: 100vw;
  height: 100vh;
  background: var(--color-neutral-0);
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--color-neutral-200);
}

.drawer-header-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-neutral-900);
}

.drawer-amount {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--color-neutral-500);
}

.drawer-close {
  background: none;
  border: none;
  padding: 6px;
  cursor: pointer;
  color: var(--color-neutral-400);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--transition-fast);
}

.drawer-close:hover {
  background: var(--color-neutral-100);
  color: var(--color-neutral-600);
}
.drawer-close:active { transform: scale(0.94); }

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.drawer-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 16px;
  color: var(--color-error-500);
  text-align: center;
}

.drawer-error p {
  margin: 0;
  font-size: 14px;
}

.retry-btn {
  background: none;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 6px 16px;
  font-size: 13px;
  color: var(--color-primary-600);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.retry-btn:hover {
  background: var(--color-primary-50);
}
.retry-btn:active { transform: scale(0.96); }

.drawer-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px 16px;
  color: var(--color-neutral-400);
  text-align: center;
}

.drawer-empty p {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.drawer-empty-hint {
  font-size: 12px;
  color: var(--color-neutral-400);
}

.drawer-summary {
  font-size: 12px;
  color: var(--color-neutral-500);
  margin-bottom: 12px;
}

.drawer-list {
  display: flex;
  flex-direction: column;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-neutral-100);
}

.history-item:last-child {
  border-bottom: none;
}

.history-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-date {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-700);
}

.history-desc {
  font-size: 12px;
  color: var(--color-neutral-500);
}

.history-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.history-amount {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-neutral-800);
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 200ms ease;
}

.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform 250ms ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer-panel,
.drawer-leave-to .drawer-panel {
  transform: translateX(100%);
}

@media (max-width: 480px) {
  .drawer-overlay {
    align-items: flex-end;
    justify-content: stretch;
  }

  .drawer-panel {
    width: 100%;
    max-height: 85vh;
    height: auto;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  }

  .drawer-enter-from .drawer-panel,
  .drawer-leave-to .drawer-panel {
    transform: translateY(100%);
  }
}
</style>

<template>
  <Teleport to="body">
    <div v-if="show" class="ph-overlay" @click.self="$emit('close')">
      <div
        ref="dropdownRef"
        class="ph-dropdown"
        :style="dropdownPosition"
        @click.stop
      >
        <div class="ph-header">
          <h3 class="ph-title">Historial de Pagos</h3>
          <button class="ph-close" @click="$emit('close')" aria-label="Cerrar">
            <X :size="16" />
          </button>
        </div>

        <div v-if="debt" class="ph-debt-info">
          <span class="ph-debt-name">{{ debt.name }}</span>
          <span class="ph-debt-balance">Saldo: ${{ fmt(debt.current_balance) }}</span>
        </div>

        <div v-if="loading" class="ph-loading">
          <div v-for="n in 3" :key="n" class="ph-payment-skeleton">
            <SkeletonLoader variant="text" width="90px" />
            <SkeletonLoader variant="text" width="120px" />
            <SkeletonLoader variant="text" width="70px" />
          </div>
        </div>

        <div v-else-if="error" class="ph-error">
          <AlertCircle :size="20" />
          <p>No pudimos cargar el historial.</p>
          <button class="ph-retry" @click="loadPayments">Intentar de nuevo</button>
        </div>

        <div v-else-if="payments.length === 0" class="ph-empty">
          <Receipt :size="28" />
          <p>No hay pagos registrados</p>
          <span class="ph-empty-hint">Registra tu primer pago para verlo aquí.</span>
        </div>

        <div v-else-if="allReversed" class="ph-empty">
          <AlertCircle :size="28" />
          <p>Todos los pagos fueron revertidos</p>
          <span class="ph-empty-hint">Los pagos aparecen aquí cuando se registran correctamente.</span>
        </div>

        <template v-else>
          <div class="ph-summary">
            <span>{{ payments.length }} {{ payments.length === 1 ? 'pago' : 'pagos' }}</span>
            <span class="ph-summary-total">${{ fmt(totalPaid) }}</span>
          </div>

          <div class="ph-list">
            <div
              v-for="payment in payments"
              :key="payment.id"
              class="ph-payment"
              :class="{ 'ph-payment-reversed': payment.is_reversed }"
            >
              <div class="ph-payment-left">
                <div class="ph-payment-date">
                  <Calendar :size="12" />
                  {{ fmtDate(payment.payment_date) }}
                </div>
                <div class="ph-payment-breakdown">
                  <span v-if="payment.principal" class="ph-principal">
                    Capital: ${{ fmt(payment.principal) }}
                  </span>
                  <span v-if="payment.interest && Number(payment.interest) > 0" class="ph-interest">
                    Interés: ${{ fmt(payment.interest) }}
                  </span>
                </div>
              </div>
              <div class="ph-payment-right">
                <div class="ph-payment-amount">${{ fmt(payment.amount) }}</div>
                <span
                  class="ph-status-badge"
                  :class="payment.is_reversed ? 'ph-reversed' : 'ph-active'"
                >
                  {{ payment.is_reversed ? 'Revertido' : 'Activo' }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { X, Calendar, Receipt, AlertCircle } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import api from '@/services/api'

const { fmt, fmtDate } = useCurrency()

const props = defineProps({
  show: { type: Boolean, default: false },
  debt: { type: Object, default: null },
  triggerRect: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const dropdownRef = ref(null)
const payments = ref([])
const loading = ref(false)
const error = ref(false)

const totalPaid = computed(() =>
  payments.value
    .filter(p => !p.is_reversed)
    .reduce((sum, p) => sum + Number(p.amount || 0), 0)
)

const allReversed = computed(() =>
  payments.value.length > 0 && payments.value.every(p => p.is_reversed)
)

const dropdownPosition = computed(() => {
  if (!props.triggerRect) return {}
  const { top, right } = props.triggerRect
  return {
    position: 'fixed',
    top: `${top + 4}px`,
    right: `${window.innerWidth - right}px`,
  }
})

async function loadPayments() {
  if (!props.debt?.id) return
  loading.value = true
  error.value = false
  try {
    const { data } = await api.get(`/debts/${props.debt.id}/payments`)
    payments.value = data
  } catch (e) {
    console.error('Error loading payments:', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

function handleKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

watch(() => props.show, (val) => {
  if (val) {
    loadPayments()
    document.addEventListener('keydown', handleKeydown)
  } else {
    document.removeEventListener('keydown', handleKeydown)
  }
})

onMounted(() => {
  if (props.show) {
    loadPayments()
    document.addEventListener('keydown', handleKeydown)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.ph-overlay {
  position: fixed;
  inset: 0;
  z-index: calc(var(--z-modal) - 1);
}

.ph-dropdown {
  width: 320px;
  max-height: 420px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: var(--z-modal);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-neutral-200);
}

.ph-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-neutral-900);
}

.ph-close {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--color-neutral-400);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ph-close:hover {
  background: var(--color-neutral-100);
  color: var(--color-neutral-600);
}

.ph-debt-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: var(--color-neutral-50);
  border-bottom: 1px solid var(--color-neutral-100);
}

.ph-debt-name {
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--color-neutral-800);
}

.ph-debt-balance {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--color-neutral-500);
}

.ph-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  font-size: 0.75rem;
  color: var(--color-neutral-500);
  border-bottom: 1px solid var(--color-neutral-100);
}

.ph-summary-total {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--color-success-600);
}

.ph-loading {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ph-payment-skeleton {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ph-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  color: var(--color-error-500);
  font-size: 0.8rem;
}

.ph-retry {
  background: none;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 4px 12px;
  font-size: 0.75rem;
  color: var(--color-primary-600);
  cursor: pointer;
}

.ph-retry:hover {
  background: var(--color-primary-50);
}

.ph-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 28px 16px;
  color: var(--color-neutral-400);
}

.ph-empty p {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 500;
}

.ph-empty-hint {
  font-size: 0.75rem;
  color: var(--color-neutral-400);
}

.ph-list {
  overflow-y: auto;
  max-height: 280px;
}

.ph-payment {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-neutral-50);
  transition: background var(--transition-fast);
}

.ph-payment:hover {
  background: var(--color-neutral-50);
}

.ph-payment:last-child {
  border-bottom: none;
}

.ph-payment-reversed {
  opacity: 0.5;
}

.ph-payment-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ph-payment-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-neutral-700);
}

.ph-payment-breakdown {
  display: flex;
  gap: 8px;
  font-size: 0.7rem;
}

.ph-principal {
  color: var(--color-neutral-500);
}

.ph-interest {
  color: var(--color-warning-600);
}

.ph-payment-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.ph-payment-amount {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-neutral-800);
}

.ph-payment-reversed .ph-payment-amount {
  text-decoration: line-through;
  color: var(--color-neutral-400);
}

.ph-status-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.ph-active {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.ph-reversed {
  background: var(--color-error-100);
  color: var(--color-error-600);
}

@media (max-width: 480px) {
  .ph-dropdown {
    width: calc(100vw - 32px);
    max-height: 60vh;
  }
}
</style>

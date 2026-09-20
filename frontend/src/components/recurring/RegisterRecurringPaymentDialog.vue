<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="close" role="dialog" aria-modal="true">
        <FocusTrap :visible="show">
          <div class="modal-content" @click.stop>
            <h3 class="modal-title">Registrar pago</h3>

            <div class="payment-summary">
              <span class="payment-name">{{ payment.name }}</span>
              <span class="payment-amount">{{ fmt(payment.amount) }}</span>
            </div>

            <p v-if="error" class="error-message">{{ error }}</p>

            <div class="modal-actions">
              <button
                data-testid="cancel-btn"
                class="btn-cancel"
                @click="close"
                :disabled="loading"
              >
                Cancelar
              </button>
              <button
                data-testid="confirm-btn"
                class="btn-confirm"
                @click="handleConfirm"
                :disabled="loading"
              >
                {{ loading ? 'Registrando...' : 'Confirmar' }}
              </button>
            </div>
          </div>
        </FocusTrap>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import FocusTrap from '@/components/FocusTrap.vue'
import { useRecurringPayments } from '@/composables/useRecurringPayments'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({
  show: { type: Boolean, default: false },
  payment: { type: Object, required: true },
})

const emit = defineEmits(['close', 'paid'])

const { getPendingEvent, executeRecurringPayment } = useRecurringPayments()
const { fmt } = useCurrency()

const loading = ref(false)
const error = ref(null)

function close() {
  if (loading.value) return
  emit('close')
}

async function handleConfirm() {
  loading.value = true
  error.value = null
  try {
    const event = await getPendingEvent(props.payment.id)
    if (!event) {
      error.value = 'No hay evento pendiente para este pago'
      return
    }
    await executeRecurringPayment(event.id)
    emit('paid')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'No se pudo registrar el pago'
  } finally {
    loading.value = false
  }
}

function onKeydown(e) {
  if (e.key === 'Escape') close()
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-content {
  background: var(--color-neutral-0);
  border-radius: 16px;
  padding: 24px;
  max-width: 400px;
  width: 100%;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: 16px;
}

.payment-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--color-neutral-50);
  border-radius: 10px;
  margin-bottom: 16px;
}

.payment-name {
  font-weight: 500;
  color: var(--color-neutral-800);
}

.payment-amount {
  font-weight: 600;
  color: var(--color-error-600);
}

.error-message {
  color: var(--color-error-600);
  font-size: 0.875rem;
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel {
  flex: 1;
  padding: 10px 16px;
  border-radius: 8px;
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
  font-family: var(--font-sans);
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: background 150ms ease;
}
.btn-cancel:hover { background: var(--color-neutral-200); }
.btn-cancel:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-confirm {
  flex: 1;
  padding: 10px 16px;
  border-radius: 8px;
  background: var(--color-primary-600);
  color: var(--color-neutral-0);
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: all 150ms ease;
}
.btn-confirm:hover { background: var(--color-primary-700); }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

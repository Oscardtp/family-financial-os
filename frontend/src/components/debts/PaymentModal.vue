<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="$emit('close')">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Pagar Deuda</h3>
            <button class="modal-close" @click="$emit('close')">&times;</button>
          </div>

          <div v-if="debt" class="debt-info">
            <span class="debt-name">{{ debt.name }}</span>
            <span class="debt-balance">Saldo: ${{ fmt(debt.current_balance ?? 0) }}</span>
          </div>

          <form class="payment-form" @submit.prevent="submitPayment">
            <div class="form-group">
              <label class="form-label">Monto del Pago</label>
              <div class="input-prefix">
                <span class="prefix">$</span>
                <input
                  :value="fmtPay.displayValue.value"
                  @input="fmtPay.onInput"
                  @focus="fmtPay.onFocus"
                  class="form-input with-prefix"
                  placeholder="0"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha del Pago</label>
              <input
                v-model="paymentForm.payment_date"
                type="date"
                class="form-input"
                required
              />
            </div>

            <p v-if="paymentError" class="form-error">{{ paymentError }}</p>

            <button type="submit" class="submit-btn" :disabled="paying">
              {{ paying ? 'Procesando...' : 'Registrar Pago' }}
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import api from '@/services/api'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  show: { type: Boolean, default: false },
  debt: { type: Object, default: null }
})

const emit = defineEmits(['close', 'paid'])

const paymentForm = reactive({
  payment_date: new Date().toISOString().split('T')[0]
})

const paying = ref(false)
const paymentError = ref('')

const fmtPay = useFormattedNumber(0, { prefix: '$' })

watch(() => props.show, (val) => {
  if (val && props.debt) {
    paymentForm.payment_date = new Date().toISOString().split('T')[0]
    fmtPay.setInitial(props.debt.minimum_payment || 0)
    paymentError.value = ''
  }
})

async function submitPayment() {
  if (!props.debt?.id || !fmtPay.rawValue.value) return

  paying.value = true
  paymentError.value = ''

  try {
    await api.post(`/debts/${props.debt.id}/payments`, {
      amount: fmtPay.rawValue.value,
      payment_date: paymentForm.payment_date
    })
    emit('paid')
    emit('close')
  } catch (e) {
    paymentError.value = e.response?.data?.detail || 'No pudimos registrar el pago. Intenta de nuevo.'
  } finally {
    paying.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--spacing-md);
}

.modal-content {
  background: var(--color-neutral-0);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  width: 100%;
  max-width: 400px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--color-neutral-900);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-neutral-500);
  line-height: 1;
}

.debt-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-neutral-50);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
}

.debt-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-neutral-800);
}

.debt-balance {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--color-neutral-600);
}

.payment-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}



.input-prefix {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.input-prefix:focus-within {
  border-color: var(--color-primary-500);
}

.prefix {
  padding: var(--spacing-md);
  background: var(--color-neutral-100);
  color: var(--color-neutral-500);
  font-size: 14px;
  font-weight: 500;
  border-right: 1px solid var(--color-neutral-200);
}

.form-input.with-prefix {
  border: none;
  border-radius: 0;
  flex: 1;
}

.form-input.with-prefix:focus {
  border: none;
}

.form-error {
  color: var(--color-error-600);
  font-size: 13px;
  margin: 0;
}

.submit-btn {
  padding: var(--spacing-md);
  background: var(--color-success-500);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-success-600);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

[data-theme="dark"] .modal-content {
  background: var(--color-neutral-100);
}
</style>
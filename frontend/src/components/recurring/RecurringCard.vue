<template>
  <div class="card" :class="payment.type === 'income' ? 'card--income' : 'card--expense'">
    <div class="card-header">
      <div class="card-info">
        <span class="card-name">{{ payment.name }}</span>
        <span class="card-frequency">{{ frequencyLabel }}</span>
      </div>
      <span class="card-amount">{{ fmt(payment.amount) }}</span>
    </div>

    <div class="card-footer">
      <span class="card-due">Vence {{ fmtMonth(payment.next_due_date) }}</span>
      <div class="card-actions">
        <button
          data-testid="history-btn"
          class="btn-icon"
          @click="$emit('open-history')"
          title="Ver historial"
        >
          <Clock :size="18" />
        </button>
        <button
          data-testid="register-payment-btn"
          class="btn-pay"
          @click="showDialog = true"
        >
          Registrar pago
        </button>
      </div>
    </div>

    <RegisterRecurringPaymentDialog
      :show="showDialog"
      :payment="payment"
      @close="showDialog = false"
      @paid="onPaid"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Clock } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import RegisterRecurringPaymentDialog from './RegisterRecurringPaymentDialog.vue'

const props = defineProps({
  payment: { type: Object, required: true },
})

const { fmt, fmtMonth } = useCurrency()
const showDialog = ref(false)

const frequencyLabel = computed(() => {
  const map = { monthly: 'Mensual', weekly: 'Semanal', biweekly: 'Quincenal', annual: 'Anual' }
  return map[props.payment.frequency] || props.payment.frequency
})

const emit = defineEmits(['open-history', 'refresh'])

function onPaid() {
  showDialog.value = false
  emit('refresh')
}
</script>

<style scoped>
.card {
  background: var(--color-neutral-0);
  border-radius: 14px;
  padding: 16px;
  border: 1px solid var(--color-neutral-100);
  transition: box-shadow 150ms ease;
}
.card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-name {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--color-neutral-900);
}

.card-frequency {
  font-size: 0.75rem;
  color: var(--color-neutral-500);
}

.card-amount {
  font-weight: 700;
  font-size: 1rem;
}

.card--expense .card-amount {
  color: var(--color-error-600);
}

.card--income .card-amount {
  color: var(--color-success-600);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-due {
  font-size: 0.8125rem;
  color: var(--color-neutral-500);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: var(--color-neutral-500);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 150ms ease;
}
.btn-icon:hover {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
}

.btn-pay {
  padding: 6px 12px;
  border-radius: 8px;
  background: var(--color-primary-600);
  color: var(--color-neutral-0);
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 0.75rem;
  cursor: pointer;
  border: none;
  transition: all 150ms ease;
}
.btn-pay:hover {
  background: var(--color-primary-700);
}
.btn-pay:active {
  transform: scale(0.97);
}
</style>

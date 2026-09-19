<template>
  <div class="recurring-card" :class="{ inactive: !payment.is_active }">
    <div class="recurring-info">
      <div class="recurring-name-row">
        <span class="recurring-name">{{ payment.name }}</span>
        <StatusBadge :variant="payment.type === 'income' ? 'success' : 'default'" :label="payment.type === 'income' ? 'Ingreso' : 'Gasto'" />
      </div>
      <span class="recurring-amount">{{ fmtFull(payment.amount) }}</span>
      <span class="recurring-freq">{{ formatFrequency(payment.frequency, payment.day_of_month) }}</span>
      <span class="recurring-next" :class="dueDate.color">
        {{ dueDate.text }}
      </span>
      <div v-if="payment.total_paid > 0" class="recurring-paid-count">
        Pagado {{ payment.total_paid }} {{ payment.total_paid === 1 ? 'vez' : 'veces' }}
        <span v-if="payment.last_paid_at" class="recurring-last-paid">
          · Último: {{ formatDateLabel(payment.last_paid_at) }}
        </span>
      </div>
    </div>
    <div class="recurring-actions">
      <button
        v-if="payment.is_active"
        class="btn-icon btn-pay"
        @click="$emit('pay', payment)"
        :title="`Pagar ${payment.name}`"
        aria-label="Pagar ahora"
      >
        <Check :size="18" />
      </button>
      <button
        class="btn-icon"
        @click="$emit('history', payment)"
        :title="`Ver historial de ${payment.name}`"
        aria-label="Ver historial"
      >
        <History :size="18" />
      </button>
      <button
        class="btn-icon"
        @click="$emit('edit', payment)"
        :title="`Editar ${payment.name}`"
        aria-label="Editar"
      >
        <Edit :size="18" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Edit, History } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import { useRecurringPayments } from '@/composables/useRecurringPayments'
import StatusBadge from '@/components/StatusBadge.vue'

const props = defineProps({
  payment: {
    type: Object,
    required: true,
  },
})

const { fmtFull } = useCurrency()
const { formatFrequency, formatDueDate } = useRecurringPayments()

const dueDate = computed(() => formatDueDate(props.payment.next_due_date))

function formatDateLabel(dateStr) {
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' })
}
</script>

<style scoped>
.recurring-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast);
}
.recurring-card.inactive {
  opacity: 0.6;
}
.recurring-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}
.recurring-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.recurring-name {
  font-weight: 600;
  color: var(--color-neutral-900);
  font-size: 0.95rem;
}
.recurring-amount {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-primary-500);
}
.recurring-freq {
  font-size: 0.8125rem;
  color: var(--color-neutral-500);
}
.recurring-next {
  font-size: 0.8125rem;
  font-weight: 500;
}
.recurring-next.error { color: var(--color-error-600); }
.recurring-next.warning { color: var(--color-warning-600); }
.recurring-paid-count {
  font-size: 0.75rem;
  color: var(--color-neutral-400);
}
.recurring-last-paid {
  font-style: italic;
}
.recurring-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}
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
.btn-icon:active { transform: scale(0.94); }
.btn-pay {
  color: var(--color-success-600);
}
.btn-pay:hover {
  background: var(--color-success-50);
  color: var(--color-success-700);
}
</style>

<template>
  <div class="expanded-content">
    <div class="debt-details">
      <div class="detail-item">
        <span class="detail-label">Saldo Actual</span>
        <span class="detail-value expense">${{ fmt(debt.current_balance) }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Total Original</span>
        <span class="detail-value">${{ fmt(debt.total_amount) }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Pago Mínimo</span>
        <span class="detail-value">${{ fmt(debt.minimum_payment) }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Tasa Interés</span>
        <span class="detail-value">{{ debt.interest_rate }}%</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Día Vencimiento</span>
        <span class="detail-value">Día {{ debt.due_day }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Fecha Inicio</span>
        <span class="detail-value">{{ fmtDate(debt.start_date) }}</span>
      </div>
    </div>

    <div class="debt-progress-section">
      <div class="progress-header">
        <span class="progress-label">Progreso de Pago</span>
        <span class="progress-percentage">{{ progressPercent }}%</span>
      </div>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" :style="{ width: `${progressPercent}%` }"></div>
      </div>
    </div>

    <DebtActions
      :debt="debt"
      @edit="$emit('edit', $event)"
      @pay="$emit('pay', $event)"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'
import DebtActions from './DebtActions.vue'

const { fmt, fmtDate } = useCurrency()

const props = defineProps({
  debt: { type: Object, required: true },
})

defineEmits(['edit', 'pay'])

const progressPercent = computed(() => {
  const original = Number(props.debt.total_amount || 0)
  const current = Number(props.debt.current_balance || 0)
  if (original <= 0) return 0
  return Math.round(((original - current) / original) * 100)
})
</script>

<style scoped>
.expanded-content {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.debt-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 11px;
  color: var(--color-neutral-400);
  text-transform: uppercase;
}

.detail-value {
  font-weight: 600;
  font-size: 13px;
  color: var(--color-neutral-800);
}

.detail-value.expense {
  color: var(--color-error-600);
  font-family: var(--font-mono);
}

.debt-progress-section {
  margin-bottom: var(--spacing-md);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}

.progress-label {
  font-size: 12px;
  color: var(--color-neutral-500);
}

.progress-percentage {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary-600);
}

.progress-bar-track {
  height: 6px;
  background: var(--color-neutral-200);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-400));
  border-radius: 3px;
  transition: width 0.5s ease;
}

@media (max-width: 640px) {
  .debt-details {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

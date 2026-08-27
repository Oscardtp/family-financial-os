<template>
  <div class="debts-summary">
    <div class="summary-card">
      <span class="summary-label">Total Deudas</span>
      <span class="summary-value expense">${{ fmt(totalDebt ?? 0) }}</span>
    </div>
    <div class="summary-card">
      <span class="summary-label">Pago Mensual</span>
      <span class="summary-value">${{ fmt(totalMonthly ?? 0) }}</span>
    </div>
    <div class="summary-card">
      <span class="summary-label">Deudas Activas</span>
      <span class="summary-value">{{ activeCount }}</span>
    </div>
    <div class="summary-card">
      <span class="summary-label">Proximo Vence</span>
      <span class="summary-value">{{ nextDue }}</span>
    </div>
  </div>
</template>

<script setup>
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

defineProps({
  totalDebt: { type: Number, default: 0 },
  totalMonthly: { type: Number, default: 0 },
  activeCount: { type: Number, default: 0 },
  nextDue: { type: String, default: '-' }
})
</script>

<style scoped>
.debts-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .debts-summary {
    grid-template-columns: repeat(4, 1fr);
  }
}

.summary-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-neutral-200);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.summary-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-500);
}

.summary-value {
  font-family: var(--font-mono);
  font-size: 22px;
  font-weight: 700;
  color: var(--color-neutral-900);
  letter-spacing: -0.02em;
}

.summary-value.expense {
  color: var(--color-error-600);
}

[data-theme="dark"] .summary-card {
  background: var(--color-neutral-100);
}
</style>

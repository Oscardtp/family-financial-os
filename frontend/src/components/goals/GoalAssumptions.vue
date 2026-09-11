<template>
  <div v-if="isInvestment" class="goal-assumptions card">
    <h4 class="assumptions-title">Supuestos</h4>
    <div class="assumptions-grid">
      <div class="assumption-item">
        <span class="assumption-label">Tasa de rendimiento</span>
        <span class="assumption-value">{{ fmtRate }}% EA</span>
      </div>
      <div class="assumption-item">
        <span class="assumption-label">Horizonte</span>
        <span class="assumption-value">{{ horizonMonths }} meses</span>
      </div>
      <div class="assumption-item">
        <span class="assumption-label">Aporte mensual</span>
        <span class="assumption-value">{{ fmtContribution }}</span>
      </div>
    </div>
    <p class="assumptions-note">Se calcula con interés compuesto mensual</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({
  goal: { type: Object, default: null },
})

const { fmt } = useCurrency()

const isInvestment = computed(() => props.goal?.goal_type === 'investment')

const fmtRate = computed(() => {
  if (!props.goal?.expected_return_rate) return '0'
  return Number(props.goal.expected_return_rate).toFixed(2)
})

const horizonMonths = computed(() => {
  if (!props.goal?.horizon_months) return '—'
  return props.goal.horizon_months
})

const fmtContribution = computed(() => {
  if (!props.goal?.monthly_contribution) return '$0'
  return fmt(props.goal.monthly_contribution)
})
</script>
<style scoped>
.goal-assumptions {
  padding: 16px;
  margin-top: 12px;
}

.assumptions-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-neutral-800);
  margin: 0 0 12px 0;
}

.assumptions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.assumption-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.assumption-label {
  font-size: 0.75rem;
  color: var(--color-neutral-500);
  text-transform: uppercase;
  font-weight: 500;
}

.assumption-value {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-neutral-900);
  font-family: var(--font-mono);
}

.assumptions-note {
  font-size: 0.75rem;
  color: var(--color-neutral-500);
  margin: 12px 0 0;
}

@media (max-width: 640px) {
  .assumptions-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>

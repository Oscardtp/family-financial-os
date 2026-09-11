<template>
  <div class="goal-projection-detail">
    <div class="projection-summary">
      <div class="summary-item">
        <span class="summary-label">Aportes totales</span>
        <span class="summary-value">{{ fmt(projection.total_contributions) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Intereses</span>
        <span class="summary-value">{{ fmt(projection.total_interest) }}</span>
      </div>
      <div v-if="projection.months_to_goal" class="summary-item">
        <span class="summary-label">Meta en</span>
        <span class="summary-value">{{ fmtMonths(projection.months_to_goal) }}</span>
      </div>
    </div>
    <GoalMonthlyBreakdown :monthly-breakdown="projection.monthly_breakdown" />
    <GoalAssumptions :goal="goal" />
    <p class="projection-disclaimer">Simulación basada en aportes regulares. Los rendimientos pasados no garantizan resultados.</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'
import GoalMonthlyBreakdown from './GoalMonthlyBreakdown.vue'
import GoalAssumptions from './GoalAssumptions.vue'

const props = defineProps({
  goal: { type: Object, default: null },
  projection: { type: Object, default: null },
})

const { fmt, fmtMonth } = useCurrency()

const projection = computed(() => props.projection || {})

function fmtMonths(months) {
  if (!months) return '—'
  if (months === 1) return '1 mes'
  return `${months} meses`
}
</script>
<style scoped>
.goal-projection-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-neutral-100);
}

.projection-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--color-neutral-500);
  text-transform: uppercase;
  font-weight: 500;
}

.summary-value {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-neutral-900);
  font-family: var(--font-mono);
}

.projection-disclaimer {
  margin-top: 12px;
  font-size: 0.75rem;
  color: var(--color-neutral-500);
  font-style: italic;
}

@media (max-width: 640px) {
  .projection-summary {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>

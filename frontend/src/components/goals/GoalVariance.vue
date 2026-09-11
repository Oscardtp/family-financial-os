<template>
  <span class="goal-variance" :class="varianceClass">
    {{ formattedVariance }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({
  projectedValue: { type: [Number, String], default: 0 },
  targetAmount: { type: [Number, String], default: 0 },
})

const { fmt } = useCurrency()

const variance = computed(() => {
  const pv = Number(props.projectedValue) || 0
  const ta = Number(props.targetAmount) || 0
  return pv - ta
})

const varianceClass = computed(() => {
  if (variance.value > 0) return 'positive'
  if (variance.value < 0) return 'negative'
  return 'neutral'
})

const formattedVariance = computed(() => {
  const prefix = variance.value > 0 ? '+' : ''
  return `${prefix}${fmt(variance.value)}`
})
</script>
<style scoped>
.goal-variance {
  font-size: 0.875rem;
  font-weight: 700;
  font-family: var(--font-mono);
}

.goal-variance.positive {
  color: var(--color-success-600);
}

.goal-variance.negative {
  color: var(--color-error-600);
}

.goal-variance.neutral {
  color: var(--color-neutral-500);
}
</style>

<template>
  <div class="progress-indicator">
    <div class="progress-header">
      <span class="progress-label">{{ label }}</span>
      <span class="progress-percentage">{{ percentage }}%</span>
    </div>
    <div class="progress-bar">
      <div
        class="progress-fill"
        :style="{ width: `${clampedPercentage}%` }"
        :class="status"
      />
    </div>
    <div class="progress-footer">
      <span class="progress-current">{{ formatCurrency(current) }}</span>
      <span class="progress-target">de {{ formatCurrency(target) }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  current: {
    type: Number,
    required: true
  },
  target: {
    type: Number,
    required: true
  },
  status: {
    type: String,
    default: 'ok',
    validator: (v) => ['ok', 'warning', 'exceeded'].includes(v)
  }
})

const percentage = computed(() => {
  if (props.target <= 0) return 0
  return Math.round((props.current / props.target) * 100)
})

const clampedPercentage = computed(() => {
  return Math.min(percentage.value, 100)
})

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}
</script>

<style scoped>
.progress-indicator {
  width: 100%;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.progress-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-neutral-700);
}

.progress-percentage {
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-neutral-600);
}

.progress-bar {
  height: 8px;
  background: var(--color-neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.progress-fill.ok {
  background: var(--color-budget-ok);
}

.progress-fill.warning {
  background: var(--color-budget-warning);
}

.progress-fill.exceeded {
  background: var(--color-budget-exceeded);
}

.progress-footer {
  display: flex;
  justify-content: space-between;
  margin-top: var(--spacing-xs);
}

.progress-current {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-neutral-700);
}

.progress-target {
  font-size: 13px;
  color: var(--color-neutral-500);
}
</style>

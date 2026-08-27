<template>
  <div class="goal-card">
    <div class="goal-header">
      <span class="goal-name">{{ goal.name }}</span>
      <span class="goal-priority" :class="'priority-' + goal.priority">{{ priorityLabel(goal.priority) }}</span>
    </div>
    <div class="goal-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }" />
      </div>
      <span class="progress-text">{{ progressPercent }}%</span>
    </div>
    <div class="goal-amounts">
      <span>Ahorrado: ${{ fmt(goal.current_amount) }}</span>
      <span>Meta: ${{ fmt(goal.target_amount) }}</span>
    </div>
    <div v-if="goal.target_date" class="goal-date">Meta: {{ formatDate(goal.target_date) }}</div>
    <div v-if="goal.target_date && goal.target_amount > goal.current_amount" class="goal-monthly-hint">
      Aporte mensual sugerido: <strong>${{ fmt(monthlySuggestion) }}</strong>
    </div>
    <div class="goal-actions">
      <button class="btn btn-outline btn-sm" @click="$emit('contribute', goal)">Contribuir</button>
      <button class="btn btn-outline btn-sm" @click="$emit('edit', goal)">Editar</button>
      <button class="btn btn-danger btn-sm" @click="$emit('delete', goal.id)">Eliminar</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'
import { useSmartCalculator } from '@/composables/useSmartCalculator'

const { fmt, formatDate } = useCurrency()
const { calculateMonthly } = useSmartCalculator()

const props = defineProps({
  goal: { type: Object, required: true },
})

defineEmits(['contribute', 'edit', 'delete'])

const progressPercent = computed(() => {
  if (!props.goal.target_amount) return 0
  return Math.min(Math.round((props.goal.current_amount / props.goal.target_amount) * 100), 100)
})

const monthlySuggestion = computed(() => {
  const remaining = props.goal.target_amount - props.goal.current_amount
  return calculateMonthly(remaining, props.goal.target_date)
})

function priorityLabel(p) {
  const map = { low: 'Baja', medium: 'Media', high: 'Alta' }
  return map[p] || p
}
</script>

<style scoped>
.goal-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-fast);
}

.goal-card:hover {
  box-shadow: var(--shadow-md);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.goal-name { font-weight: 600; font-size: 0.95rem; color: var(--color-neutral-900); }
.goal-priority { font-size: 0.75rem; font-weight: 500; }
.priority-low { color: var(--color-neutral-400); }
.priority-medium { color: var(--color-warning-600); }
.priority-high { color: var(--color-error-600); }

.goal-progress {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--color-neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary-500);
  border-radius: var(--radius-full);
  transition: width var(--transition-normal);
}

.progress-text { font-size: 0.8rem; font-weight: 600; color: var(--color-primary-600); min-width: 36px; }

.goal-amounts {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-neutral-400);
  margin-bottom: var(--spacing-xs);
}

.goal-date {
  font-size: 0.75rem;
  color: var(--color-neutral-400);
  margin-bottom: var(--spacing-xs);
}

.goal-monthly-hint {
  font-size: 0.75rem;
  color: var(--color-success-600);
  margin-bottom: var(--spacing-md);
}

.goal-actions {
  display: flex;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-sm);
}

.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }

.btn-outline {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  color: var(--color-neutral-700);
}

.btn-outline:hover { border-color: var(--color-primary-400); color: var(--color-primary-600); }

.btn-danger {
  background: var(--color-error-600);
  color: white;
}

.btn-danger:hover:not(:disabled) { background: var(--color-error-700); }
</style>

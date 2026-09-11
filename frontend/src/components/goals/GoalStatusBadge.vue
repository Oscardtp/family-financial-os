<template>
  <span class="goal-status-badge" :class="statusClass">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  onTrack: { type: Boolean, default: null },
  completed: { type: Boolean, default: false },
})

const statusClass = computed(() => {
  if (props.completed) return 'completed'
  if (props.onTrack === true) return 'on-track'
  if (props.onTrack === false) return 'at-risk'
  return 'unknown'
})

const label = computed(() => {
  if (props.completed) return 'Lograda'
  if (props.onTrack === true) return 'En buen camino'
  if (props.onTrack === false) return 'Revisa tu aporte'
  return 'Sin datos'
})
</script>
<style scoped>
.goal-status-badge {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  min-height: 22px;
}

.goal-status-badge.on-track {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.goal-status-badge.at-risk {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.goal-status-badge.completed {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.goal-status-badge.unknown {
  background: var(--color-neutral-100);
  color: var(--color-neutral-600);
}
</style>

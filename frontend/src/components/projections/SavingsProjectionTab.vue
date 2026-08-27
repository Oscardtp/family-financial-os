<template>
  <div class="tab-content">
    <div v-for="g in goals" :key="g.id" class="card">
      <h3>{{ g.name }}</h3>
      <div class="savings-grid">
        <div><span class="label">Objetivo</span><span class="value">${{ fmt(g.target) }}</span></div>
        <div><span class="label">Actual</span><span class="value income">${{ fmt(g.current) }}</span></div>
        <div><span class="label">Progreso</span><span class="value">{{ g.percentage.toFixed(1) }}%</span></div>
        <div><span class="label">Restante</span><span class="value">${{ fmt(g.remaining) }}</span></div>
        <div><span class="label">Meses restantes</span><span class="value">{{ g.months_to_goal || 'N/A' }}</span></div>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :class="g.on_track ? 'on-track' : 'off-track'" :style="{ width: Math.min(g.percentage, 100) + '%' }" />
      </div>
    </div>
    <p v-if="!goals?.length" class="empty">Sin metas de ahorro</p>
  </div>
</template>

<script setup>
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

defineProps({
  goals: { type: Array, default: () => [] },
})
</script>

<style scoped>
.tab-content { display: flex; flex-direction: column; gap: var(--spacing-md); animation: fadeIn 200ms ease; }
.card h3 { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--spacing-md); }
.savings-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-md); }
.savings-grid > div { display: flex; flex-direction: column; gap: 2px; }
.label { font-size: 0.75rem; color: var(--color-neutral-500); }
.value { font-size: 0.9rem; font-weight: 600; font-family: var(--font-mono); color: var(--color-neutral-900); }
.value.income { color: var(--color-success-600); }
.progress-bar { height: 8px; background: var(--color-neutral-100); border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 4px; transition: width 500ms ease; }
.progress-fill.on-track { background: var(--color-success-500); }
.progress-fill.off-track { background: var(--color-warning-500); }
.empty { color: var(--color-neutral-400); text-align: center; padding: var(--spacing-lg); font-size: 0.875rem; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>

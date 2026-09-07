<template>
  <div>
    <div v-if="loading" class="list-loading">
      <div v-for="n in 5" :key="n" class="skeleton-day-group"></div>
    </div>
    <div v-else-if="groups.length === 0" class="empty-state">
      <p class="empty-title">No hay eventos este mes</p>
      <p class="empty-desc">Cuando agregues un pago o una obligación, aparecerá aquí.</p>
      <button class="empty-cta" @click="$emit('createOnDate', todayStr)">Crear evento</button>
    </div>
    <div v-else class="list-view">
      <div v-for="group in groups" :key="group.dateStr" class="day-group">
        <div class="day-header">
          <span class="day-num">{{ group.dayNum }}</span>
          <span class="day-label">{{ group.dayLabel }}</span>
        </div>
        <button
          v-for="ev in group.events"
          :key="ev.id"
          class="list-item"
          @click="$emit('openEvent', ev)"
        >
          <span class="list-dot" :class="eventColor(ev)"></span>
          <span class="list-title">{{ ev.title }}</span>
          <span class="list-amount">${{ fmt(ev.amount) }}</span>
          <span v-if="ev.notes" class="list-note">{{ ev.notes }}</span>
          <ChevronRight :size="16" class="list-chevron" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ChevronRight } from 'lucide-vue-next'

defineProps({
  groups: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  todayStr: { type: String, required: true },
  eventColor: { type: Function, required: true },
  fmt: { type: Function, required: true },
})

defineEmits(['openEvent', 'createOnDate'])
</script>

<style scoped>
.day-group { margin-bottom: var(--spacing-md); }
.day-header {
  display: flex; align-items: baseline; gap: var(--spacing-sm);
  padding: var(--spacing-xs) 0 var(--spacing-sm); border-bottom: 1.5px solid var(--color-neutral-200);
  margin-bottom: var(--spacing-xs);
}
.day-num { font-size: 1.3rem; font-weight: 800; color: var(--color-neutral-800); }
.day-label { font-size: 0.85rem; color: var(--color-neutral-500); text-transform: capitalize; }
.list-item {
  display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-sm) var(--spacing-md);
  border: 1.5px solid var(--color-neutral-200); border-radius: var(--radius-lg);
  background: var(--color-neutral-0); cursor: pointer; transition: all var(--transition-fast);
  width: 100%; text-align: left;
}
.list-item:hover { border-color: var(--color-primary-300); box-shadow: var(--shadow-xs); }
.list-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
.list-dot.ev-income { background: var(--color-calendar-income); }
.list-dot.ev-expense { background: var(--color-calendar-expense); }
.list-dot.ev-debt { background: var(--color-calendar-debt); }
.list-dot.ev-goal { background: var(--color-calendar-goal); }
.list-dot.ev-paid { background: var(--color-calendar-paid); }
.list-dot.ev-overdue { background: var(--color-calendar-overdue); }
.list-dot.ev-upcoming { background: var(--color-calendar-upcoming); }
.list-dot.ev-default { background: var(--color-calendar-default); }
.list-title { flex: 1; font-weight: 600; font-size: 0.9rem; color: var(--color-neutral-800); }
.list-amount { font-weight: 700; font-size: 0.9rem; color: var(--color-neutral-700); }
.list-note { font-size: 0.75rem; color: var(--color-neutral-500); max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.list-chevron { color: var(--color-neutral-400); flex-shrink: 0; }
.list-loading { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.skeleton-day-group { height: 80px; background: var(--color-neutral-100); border-radius: var(--radius-lg); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state { text-align: center; padding: var(--spacing-2xl) var(--spacing-md); }
.empty-title { font-size: 1rem; font-weight: 700; color: var(--color-neutral-700); margin-bottom: var(--spacing-xs); }
.empty-desc { font-size: 0.85rem; color: var(--color-neutral-500); margin-bottom: var(--spacing-md); }
.empty-cta {
  display: inline-flex; padding: var(--spacing-sm) var(--spacing-lg); border: none;
  border-radius: var(--radius-full); background: var(--color-primary-500); color: #fff;
  font-weight: 600; cursor: pointer; transition: background var(--transition-fast);
}
.empty-cta:hover { background: var(--color-primary-600); }
</style>

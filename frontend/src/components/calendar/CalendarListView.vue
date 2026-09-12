<template>
  <div class="calendar-list-view">
    <div v-if="loading" class="list-loading">
      <div v-for="n in 5" :key="n" class="skeleton-day-group"></div>
    </div>

    <div v-else-if="groups.length === 0" class="empty-state">
      <p class="empty-title">No hay eventos este mes</p>
      <p class="empty-desc">Cuando agregues un pago o una obligación, aparecerá aquí.</p>
      <button class="empty-cta" @click="$emit('createOnDate', todayStr)">Crear evento</button>
    </div>

    <div v-else class="timeline">
      <div v-for="group in groups" :key="group.dateStr" class="day-group" :class="{ 'is-today': group.dateStr === todayStr }">
        <div class="day-dot"></div>
        <div class="day-label">{{ group.dateStr === todayStr ? 'HOY' : group.dayLabel }}</div>
        <button
          v-for="ev in group.events"
          :key="ev.id"
          class="entry"
          @click="$emit('openEvent', ev)"
        >
          <div class="entry-left">
            <div class="entry-icon">
              <component :is="typeIcon(ev.type)" :size="16" />
            </div>
            <div class="entry-body">
              <div class="entry-name">{{ ev.title }}</div>
              <div v-if="ev.notes" class="entry-sub">{{ ev.notes }}</div>
              <div v-else-if="statusLabel(ev) !== 'Pendiente'" class="entry-sub">{{ statusLabel(ev) }}</div>
            </div>
          </div>
          <span class="entry-amount" :class="eventColor(ev)">{{ fmtAmount(ev.amount) }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  TrendingUp, Target, CreditCard, Wallet, Bell,
} from 'lucide-vue-next'
import {
  statusLabel as _statusLabel,
  typeIcon as _typeIcon,
} from '@/composables/useCalendarHelpers'

defineProps({
  groups: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  todayStr: { type: String, required: true },
  eventColor: { type: Function, required: true },
  fmt: { type: Function, required: true },
})

defineEmits(['openEvent', 'createOnDate'])

function statusLabel(ev) { return _statusLabel(ev) }
function typeIcon(type) { return _typeIcon(type, { TrendingUp, Target, CreditCard, Wallet, Bell }) }
function fmtAmount(amount) {
  const n = Number(amount)
  if (Number.isNaN(n)) return '$0'
  const abs = Math.abs(n).toLocaleString('es-CO')
  return (n < 0 ? '-$' : '$') + abs
}
</script>

<style scoped>
.calendar-list-view { padding: var(--spacing-md); max-width: 980px; margin: 0 auto; }

.timeline { position: relative; padding-left: 22px; }
.timeline::before {
  content: ''; position: absolute; left: 5px; top: 6px; bottom: 6px;
  width: 1px; background: var(--color-neutral-200);
}

.day-group { position: relative; margin-bottom: var(--spacing-lg); }
.day-group:last-child { margin-bottom: 0; }

.day-dot {
  position: absolute; left: -22px; top: 4px;
  width: 11px; height: 11px; border-radius: 50%;
  background: var(--color-neutral-0); border: 1.5px solid var(--color-neutral-400);
}
.day-group.is-today .day-dot { border-color: var(--color-error-500); background: var(--color-error-500); }

.day-label {
  font-size: var(--font-size-3xs); font-weight: 700; color: var(--color-neutral-500);
  letter-spacing: 0.4px; margin-bottom: var(--spacing-sm); text-transform: uppercase;
}
.day-group.is-today .day-label { color: var(--color-error-500); }

.entry {
  display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-sm);
  width: 100%; padding: var(--spacing-sm) 0; border: none; background: transparent;
  text-align: left; cursor: pointer; border-bottom: 1px solid var(--color-neutral-200);
  transition: background var(--transition-fast);
}
.entry:last-child { border-bottom: none; }
.entry:hover { background: var(--color-neutral-50); }

.entry-left { display: flex; align-items: center; gap: var(--spacing-sm); flex: 1; min-width: 0; }
.entry-icon {
  width: 32px; height: 32px; border-radius: var(--radius-md);
  background: var(--color-neutral-100); display: inline-flex; align-items: center; justify-content: center;
  color: var(--color-neutral-600); flex-shrink: 0;
}
.entry-body { min-width: 0; }
.entry-name {
  font-size: var(--font-size-sm-alt); font-weight: 600; color: var(--color-neutral-800);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.entry-sub { font-size: var(--font-size-3xs); color: var(--color-neutral-500); margin-top: 1px; }

.entry-amount {
  font-family: var(--font-mono); font-size: var(--font-size-sm-alt); font-weight: 700;
  color: var(--color-neutral-700); white-space: nowrap; flex-shrink: 0;
}
.entry-amount.ev-income { color: var(--color-success-700); }
.entry-amount.ev-expense { color: var(--color-error-700); }
.entry-amount.ev-debt { color: var(--color-warning-700); }
.entry-amount.ev-goal { color: var(--color-secondary-700); }
.entry-amount.ev-paid { color: var(--color-success-700); }
.entry-amount.ev-overdue { color: var(--color-error-700); }
.entry-amount.ev-upcoming { color: var(--color-warning-700); }
.entry-amount.ev-default { color: var(--color-neutral-700); }

.list-loading { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.skeleton-day-group { height: 80px; background: var(--color-neutral-100); border-radius: var(--radius-lg); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state { text-align: center; padding: var(--spacing-2xl) var(--spacing-md); }
.empty-title { font-size: var(--font-size-base); font-weight: 600; color: var(--color-neutral-700); margin-bottom: var(--spacing-xs); }
.empty-desc { font-size: var(--font-size-sm-alt); color: var(--color-neutral-500); margin-bottom: var(--spacing-md); }
.empty-cta {
  display: inline-flex; padding: var(--spacing-sm) var(--spacing-lg); border: none;
  border-radius: var(--radius-full); background: var(--color-primary-500); color: #fff;
  font-weight: 600; cursor: pointer; transition: background var(--transition-fast);
}
.empty-cta:hover { background: var(--color-primary-600); }

@media (max-width: 767px) {
  .calendar-list-view { padding: var(--spacing-sm); }
  .timeline { padding-left: 18px; }
  .timeline::before { left: 4px; }
  .day-dot { left: -18px; width: 9px; height: 9px; }
  .entry { padding: var(--spacing-sm) 0; }
  .entry-icon { width: 28px; height: 28px; }
}
</style>

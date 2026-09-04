<template>
  <div>
    <div class="cal-weekdays">
      <span v-for="day in weekdays" :key="day" class="cal-weekday">{{ day }}</span>
    </div>

    <div v-if="loading" class="cal-grid">
      <div v-for="n in 42" :key="n" class="cal-cell skeleton-cell"></div>
    </div>

    <div v-else class="cal-grid">
      <div
        v-for="(cell, i) in days"
        :key="i"
        class="cal-cell"
        :class="{ 'out-month': !cell.inMonth, 'is-today': cell.isToday }"
        @click.self="$emit('createOnDate', cell.dateStr)"
      >
        <span class="cell-day" :class="{ 'today-pill': cell.isToday }" @click.stop>{{ cell.day }}</span>
        <div class="cell-events">
          <button
            v-for="ev in cell.events"
            :key="ev.id"
            class="ev-chip"
            :class="eventColor(ev)"
            @click.stop="$emit('openEvent', ev)"
          >
            <span class="ev-title">{{ ev.title }}</span>
            <span v-if="ev.recommended_date && ev.due_date !== ev.recommended_date" class="ev-sub">{{ fmtDateShort(ev.recommended_date) }}</span>
            <span v-if="isCutoffUrgent(ev)" class="ev-cutoff-badge">🔴</span>
            <span v-if="ev.confidence < 100" class="ev-conf-badge">?</span>
            <span class="ev-amount">{{ fmt(ev.amount) }}</span>
          </button>
        </div>
      </div>
    </div>

    <p v-if="!loading && days.every(c => c.events.length === 0) && days.some(c => c.inMonth)" class="empty-state-inline">
      Este mes está tranquilo. Cuando agregues un pago o una obligación, aparecerá aquí.
    </p>
  </div>
</template>

<script setup>
defineProps({
  days: { type: Array, required: true },
  weekdays: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  eventColor: { type: Function, required: true },
  fmtDateShort: { type: Function, required: true },
  isCutoffUrgent: { type: Function, required: true },
  fmt: { type: Function, required: true },
})

defineEmits(['createOnDate', 'openEvent'])
</script>

<style scoped>
.cal-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin-bottom: 6px; }
.cal-weekday {
  text-align: center; font-size: var(--font-size-xs, 0.75rem); font-weight: 700;
  color: var(--color-neutral-400); padding: 4px 0; text-transform: uppercase;
}
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
.cal-cell {
  background: var(--color-neutral-0); border: 1.5px solid var(--color-neutral-200);
  border-radius: var(--radius-lg); min-height: 96px; padding: 6px;
  display: flex; flex-direction: column; gap: 4px;
}
.out-month { background: var(--color-neutral-50); opacity: 0.6; }
.is-today { border-color: var(--color-primary-500); }
.cell-day { font-size: 0.8rem; font-weight: 600; color: var(--color-neutral-500); }
.today-pill {
  background: var(--color-primary-500); color: #fff; border-radius: 50%;
  width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center;
}
.cell-events { display: flex; flex-direction: column; gap: 3px; overflow: hidden; }

.ev-chip {
  display: flex; align-items: center; gap: 4px; border: none; cursor: pointer;
  border-radius: var(--radius-sm); padding: 3px 6px; font-size: 0.72rem;
  text-align: left; color: var(--color-neutral-800); transition: filter var(--transition-fast);
}
.ev-chip:hover { filter: brightness(0.95); }
.ev-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ev-sub { font-size: 0.65rem; color: var(--color-neutral-500); white-space: nowrap; }
.ev-cutoff-badge { font-size: 0.6rem; }
.ev-conf-badge {
  font-size: 0.6rem; background: var(--color-neutral-200); border-radius: 50%;
  width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center; font-weight: 700;
}
.ev-amount { margin-left: auto; font-weight: 700; }
.ev-income { background: var(--color-calendar-income-bg); }
.ev-expense { background: var(--color-calendar-expense-bg); }
.ev-debt { background: var(--color-calendar-debt-bg); }
.ev-goal { background: var(--color-calendar-goal-bg); }
.ev-paid { background: var(--color-calendar-paid-bg); }
.ev-overdue { background: var(--color-calendar-overdue-bg); }
.ev-upcoming { background: var(--color-calendar-upcoming-bg); }
.ev-default { background: var(--color-calendar-default-bg); }

.skeleton-cell { background: var(--color-neutral-100); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state-inline { text-align: center; color: var(--color-neutral-400); margin-top: var(--spacing-lg); font-size: 0.85rem; }
</style>

<template>
  <div class="calendar-grid-view">
    <div class="cal-header">
      <div class="cal-nav">
        <button class="cal-nav-btn" @click="$emit('prev')" aria-label="Mes anterior"><ChevronLeft :size="16" /></button>
        <button class="cal-nav-btn" @click="$emit('next')" aria-label="Mes siguiente"><ChevronRight :size="16" /></button>
        <h2 class="cal-month">{{ monthLabel }}</h2>
      </div>
      <div class="cal-filters">
        <button
          v-for="f in FILTERS"
          :key="f.key"
          class="cal-filter-chip"
          :class="{ 'cal-filter-chip--active': filter === f.key }"
          @click="$emit('update:filter', f.key)"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <div class="cal-weekdays">
      <span v-for="day in WEEKDAYS" :key="day" class="cal-weekday">{{ day }}</span>
    </div>

    <div v-if="loading" class="cal-grid">
      <div v-for="n in 42" :key="n" class="cal-cell skeleton-cell"></div>
    </div>

    <div v-else class="cal-grid">
      <div
        v-for="(cell, i) in days"
        :key="i"
        class="cal-cell"
        :class="{
          'out-month': !cell.inMonth,
          'is-today': cell.isToday,
          'is-selected': cell.dateStr === selectedDate,
          'has-events': cell.events.length > 0,
        }"
        :aria-label="cellAriaLabel(cell)"
        @click="() => handleCellClick(cell)"
      >
        <span class="cell-day">{{ cell.day }}</span>
        <div v-if="cell.events.length" class="cal-dot-row">
          <span
            v-for="ev in cell.events"
            :key="ev.id"
            class="cal-dot"
            :class="eventColor(ev)"
          ></span>
        </div>
      </div>
    </div>

    <p v-if="!loading && days.every(c => c.events.length === 0) && days.some(c => c.inMonth)" class="empty-state-inline">
      Este mes está tranquilo. Cuando agregues un pago o una obligación, aparecerá aquí.
    </p>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const WEEKDAYS = ['L', 'M', 'M', 'J', 'V', 'S', 'D']

const FILTERS = [
  { key: 'all', label: 'Todo' },
  { key: 'income', label: 'Ingresos' },
  { key: 'expense', label: 'Gastos' },
  { key: 'debt', label: 'Pagos' },
  { key: 'goal', label: 'Metas' },
]

defineProps({
  days: { type: Array, required: true },
  monthLabel: { type: String, required: true },
  loading: { type: Boolean, default: false },
  selectedDate: { type: String, default: '' },
  filter: { type: String, default: 'all' },
  eventColor: { type: Function, required: true },
})

const emit = defineEmits(['selectDay', 'createOnDate', 'prev', 'next', 'today', 'update:filter'])

const TYPE_LABELS = {
  income: 'Ingreso',
  expense: 'Gasto',
  debt: 'Pago',
  goal: 'Meta',
}

function cellAriaLabel(cell) {
  if (!cell.events.length) return ''
  const types = [...new Set(cell.events.map(e => TYPE_LABELS[e.type] || 'Evento'))]
  const count = cell.events.length
  return `${cell.day} de ${cell.monthName || ''}: ${count} ${count === 1 ? 'evento' : 'eventos'}: ${types.join(', ')}`
}

function handleCellClick(cell) {
  if (cell.events.length > 0) {
    emit('selectDay', cell.dateStr)
  } else {
    emit('createOnDate', cell.dateStr)
  }
}
</script>

<style scoped>
.calendar-grid-view { padding: var(--spacing-md); max-width: 980px; margin: 0 auto; }

.cal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: var(--spacing-md); padding: 0 var(--spacing-sm); gap: var(--spacing-sm); flex-wrap: wrap;
}
.cal-nav { display: flex; align-items: center; gap: var(--spacing-xs); }
.cal-month {
  font-family: var(--font-display); font-size: var(--font-size-lg); font-weight: 600;
  color: var(--color-neutral-800); margin: 0; text-transform: capitalize;
}
.cal-nav-btn {
  display: inline-flex; align-items: center; justify-content: center;
  height: 44px; min-width: 44px; padding: 0 var(--spacing-sm); border: 1px solid var(--color-neutral-200);
  background: var(--color-neutral-0); color: var(--color-neutral-700);
  border-radius: var(--radius-sm); cursor: pointer; font-size: var(--font-size-xs-alt);
  font-weight: 500; transition: background var(--transition-fast);
}
.cal-nav-btn:hover { background: var(--color-neutral-100); }

.cal-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.cal-filter-chip {
  padding: 8px 14px; border-radius: var(--radius-pill); border: 1px solid var(--color-neutral-200);
  background: var(--color-neutral-0); color: var(--color-neutral-700); font-size: var(--font-size-3xs);
  font-weight: 600; cursor: pointer; transition: all var(--transition-fast); white-space: nowrap;
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center;
}
.cal-filter-chip:hover { background: var(--color-neutral-50); }
.cal-filter-chip--active { background: var(--color-neutral-900); color: var(--color-neutral-0); border-color: var(--color-neutral-900); }

.cal-weekdays {
  display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px;
  padding: 0 var(--spacing-sm) var(--spacing-sm);
}
.cal-weekday {
  text-align: center; font-size: var(--font-size-3xs); font-weight: 700;
  color: var(--color-neutral-500); padding: 8px 0; text-transform: uppercase;
}

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; padding: 0 var(--spacing-sm); }
.cal-cell {
  min-height: 0; aspect-ratio: 1 / 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
  border-radius: var(--radius-lg); background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200); cursor: default;
  transition: background var(--transition-fast), border-color var(--transition-fast);
  position: relative; gap: 4px; padding: 8px;
}
.cal-cell::after {
  content: '';
  position: absolute;
  inset: 6px;
  border-radius: var(--radius-md);
}
.cal-cell.has-events { cursor: pointer; }
.cal-cell.has-events:hover { background: var(--color-neutral-50); }
.cal-cell.out-month { opacity: 0.35; }
.cal-cell.is-today { border-color: var(--color-primary-500); box-shadow: inset 0 0 0 1px var(--color-primary-500); }
.cal-cell.is-selected { outline: 2px solid var(--color-warning-500); outline-offset: -2px; }

.cell-day {
  font-size: var(--font-size-xs-alt); font-weight: 700; color: var(--color-neutral-600);
  width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;
  border-radius: var(--radius-full);
  position: relative;
  z-index: 1;
}
.cal-cell.is-today .cell-day {
  background: var(--color-primary-500); color: #fff;
}

.cal-dot-row { display: flex; gap: 4px; margin-top: 6px; height: 8px; align-items: center; flex-wrap: wrap; justify-content: center; }
.cal-dot { width: 8px; height: 8px; border-radius: 50%; }
.cal-dot.ev-income { background: var(--color-calendar-income); }
.cal-dot.ev-expense { background: var(--color-calendar-expense); }
.cal-dot.ev-debt { background: var(--color-calendar-debt); }
.cal-dot.ev-goal { background: var(--color-calendar-goal); }
.cal-dot.ev-paid { background: var(--color-calendar-paid); }
.cal-dot.ev-overdue { background: var(--color-calendar-overdue); }
.cal-dot.ev-upcoming { background: var(--color-calendar-upcoming); }
.cal-dot.ev-default { background: var(--color-calendar-default); }

.skeleton-cell { background: var(--color-neutral-100); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state-inline {
  text-align: center; color: var(--color-neutral-500); margin-top: var(--spacing-lg);
  font-size: var(--font-size-sm-alt);
}

@media (max-width: 1023px) {
  .calendar-grid-view { padding: var(--spacing-sm); }
  .cal-header { padding: 0; margin-bottom: var(--spacing-sm); }
  .cal-month { font-size: var(--font-size-base); }
  .cal-grid { gap: 3px; padding: 0 var(--spacing-xs); }
  .cal-weekdays { padding: 0 var(--spacing-xs) var(--spacing-xs); gap: 3px; }
  .cal-cell { padding: 6px; }
  .cell-day { width: 26px; height: 26px; font-size: 0.75rem; }
  .cal-dot { width: 7px; height: 7px; }
}
@media (max-width: 767px) {
  .calendar-grid-view { padding: var(--spacing-sm); }
  .cal-header { flex-direction: column; align-items: stretch; gap: var(--spacing-sm); }
  .cal-month { text-align: center; font-size: var(--font-size-base); }
  .cal-nav { justify-content: center; }
  .cal-filters { justify-content: center; }
  .cal-weekdays { padding: 0 0 var(--spacing-xs); }
  .cal-grid {
    grid-template-columns: repeat(7, 1fr); gap: 2px; padding: 0;
    width: 100%;
  }
  .cal-cell {
    border-radius: var(--radius-sm); padding: 4px;
    aspect-ratio: 1 / 1; min-height: 0;
    flex-direction: column; align-items: center; justify-content: flex-start;
  }
  .cell-day { width: 24px; height: 24px; font-size: 0.7rem; }
  .cal-dot-row { margin-top: 4px; gap: 2px; }
  .cal-dot { width: 6px; height: 6px; }
  .cal-cell:first-child { border-top: 1px solid var(--color-neutral-200); }
}
</style>

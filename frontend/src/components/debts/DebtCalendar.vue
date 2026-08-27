<template>
  <div class="debt-calendar">
    <div class="calendar-legend">
      <span class="legend-item">
        <span class="legend-dot paid"></span> Pagado
      </span>
      <span class="legend-item">
        <span class="legend-dot pending"></span> Pendiente
      </span>
      <span class="legend-item">
        <span class="legend-dot reversed"></span> Revertido
      </span>
    </div>

    <div v-if="loading" class="calendar-loading">
      <span>Cargando calendario...</span>
    </div>

    <div v-else class="calendar-grid">
      <div
        v-for="(month, idx) in months"
        :key="idx"
        class="calendar-month"
        :class="getMonthClass(month.num, month.year)"
        :data-tooltip="getMonthTooltip(month)"
        @click="handleClick(month)"
      >
        <span class="month-name">{{ month.name }}</span>
        <span class="month-amount">${{ fmt(debt.minimum_payment ?? 0) }}</span>
        <span class="month-status" :class="getMonthClass(month.num, month.year)">
          <span v-if="getMonthClass(month.num, month.year) === 'paid'">&#10003;</span>
          <span v-else-if="getMonthClass(month.num, month.year) === 'reversed'">&#10007;</span>
          <span v-else>&#9675;</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  debt: { type: Object, required: true },
  paymentHistory: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['month-click'])

const currentYear = new Date().getFullYear()

const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
const monthFullNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const months = computed(() => {
  return monthNames.map((name, idx) => ({
    name,
    num: idx + 1,
    year: currentYear
  }))
})

function getMonthClass(monthNum, year) {
  const record = props.paymentHistory.find(
    r => r.year === year && r.month === monthNum
  )
  if (!record) return ''
  return record.status
}

function getMonthTooltip(month) {
  const status = getMonthClass(month.num, month.year)
  const label = status === 'paid' ? 'Pagado' : status === 'reversed' ? 'Revertido' : status === 'pending' ? 'Pendiente' : 'Sin registro'
  return `${monthFullNames[month.num - 1]} ${month.year}: ${label}`
}

function handleClick(month) {
  const status = getMonthClass(month.num, month.year)
  if (status === 'pending') {
    emit('month-click', { month: month.num, year: month.year, status })
  }
}
</script>

<style scoped>
.debt-calendar {
  padding: 0;
}

.calendar-legend {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 12px;
  color: var(--color-neutral-500);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.paid {
  background: var(--color-success-500);
}

.legend-dot.pending {
  background: var(--color-neutral-300);
}

.legend-dot.reversed {
  background: var(--color-warning-500);
}

.calendar-loading {
  text-align: center;
  padding: var(--spacing-lg);
  color: var(--color-neutral-400);
  font-size: 13px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 2px;
}

.calendar-month {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-sm) var(--spacing-xs);
  min-height: 64px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: 4px;
  cursor: default;
  transition: all 0.15s ease;
}

.calendar-month.paid {
  background: #e6f4ea;
  border-color: #ceead6;
}

.calendar-month.pending {
  cursor: pointer;
}

.calendar-month.pending:hover {
  background: #e8f0fe;
  border-color: #d2e3fc;
}

.calendar-month.reversed {
  background: #fce8e6;
  border-color: #f5c6cb;
}

.calendar-month.pending:active {
  transform: scale(0.97);
}

.calendar-month[data-tooltip]:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 8px;
  background: var(--color-neutral-900);
  color: white;
  font-size: 11px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 10;
}

.month-name {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-neutral-600);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.month-amount {
  font-size: 10px;
  color: var(--color-neutral-400);
  margin-bottom: 4px;
}

.month-status {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.month-status.paid {
  background: #1e8e3e;
  color: white;
}

.month-status.pending {
  background: var(--color-neutral-200);
  color: var(--color-neutral-500);
}

.month-status.reversed {
  background: #d93025;
  color: white;
}
</style>
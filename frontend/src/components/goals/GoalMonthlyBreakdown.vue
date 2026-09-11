<template>
  <div class="goal-monthly-breakdown">
    <button class="breakdown-toggle" @click="open = !open">
      <span>{{ open ? 'Ocultar' : 'Ver' }} desglose mensual</span>
      <span class="toggle-icon" :class="{ open }">▾</span>
    </button>
    <div v-if="open" class="breakdown-table-wrapper">
      <table class="breakdown-table">
        <thead>
          <tr>
            <th>Mes</th>
            <th>Aporte</th>
            <th>Interés</th>
            <th>Saldo</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in rows" :key="idx">
            <td>{{ row.month }}</td>
            <td>{{ fmt(row.contribution) }}</td>
            <td>{{ fmt(row.interest) }}</td>
            <td>{{ fmt(row.balance) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({
  monthlyBreakdown: { type: Array, default: () => [] },
})

const { fmt } = useCurrency()
const open = ref(false)

const rows = computed(() => {
  return (props.monthlyBreakdown || []).map((item) => ({
    month: item.month || '',
    contribution: Number(item.contribution) || 0,
    interest: Number(item.interest) || 0,
    balance: Number(item.balance) || 0,
  }))
})
</script>
<style scoped>
.goal-monthly-breakdown {
  margin-top: 12px;
}

.breakdown-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  color: var(--color-primary-600);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  padding: 4px 0;
  min-height: 44px;
}

.breakdown-toggle:hover {
  color: var(--color-primary-700);
}

.toggle-icon {
  transition: transform var(--transition-fast);
  font-size: 0.75rem;
}

.toggle-icon.open {
  transform: rotate(180deg);
}

.breakdown-table-wrapper {
  overflow-x: auto;
  margin-top: 8px;
}

.breakdown-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.breakdown-table th {
  text-align: left;
  padding: 8px;
  border-bottom: 2px solid var(--color-neutral-200);
  color: var(--color-neutral-500);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
}

.breakdown-table td {
  padding: 8px;
  border-bottom: 1px solid var(--color-neutral-100);
  color: var(--color-neutral-700);
  font-family: var(--font-mono);
}

.breakdown-table tr:last-child td {
  border-bottom: none;
}

@media (max-width: 640px) {
  .breakdown-table th,
  .breakdown-table td {
    padding: 6px 4px;
    font-size: 0.75rem;
  }
}
</style>

<template>
  <div class="tab-content">
    <div class="card">
      <h3>Proyección de Flujo de Caja ({{ cashFlow.months }} meses)</h3>
      <div v-if="cashFlow.projections?.length" class="chart-container">
        <div v-for="p in cashFlow.projections" :key="p.month" class="projection-row">
          <span class="month-label">Mes {{ p.month }}</span>
          <div class="bar-group">
            <div class="bar income" :style="{ width: barWidth(p.income, maxVal) + '%' }" />
            <div class="bar expense" :style="{ width: barWidth(p.expenses, maxVal) + '%' }" />
          </div>
          <span class="amount">${{ fmt(p.net_income) }}</span>
        </div>
      </div>
      <p v-else class="empty">Sin movimientos de efectivo</p>
      <div class="summary-footer">
        <span>Ahorro proyectado: <strong>${{ fmt(cashFlow.projected_savings) }}</strong></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

defineProps({
  cashFlow: { type: Object, required: true },
  maxVal: { type: Number, default: 1 },
  barWidth: { type: Function, required: true },
})
</script>

<style scoped>
.tab-content { animation: fadeIn 200ms ease; }
.card h3 { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--spacing-md); }
.empty { color: var(--color-neutral-400); text-align: center; padding: var(--spacing-lg); font-size: 0.875rem; }
.chart-container { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.projection-row { display: grid; grid-template-columns: 70px 1fr 80px; align-items: center; gap: var(--spacing-sm); }
.month-label { font-size: 0.75rem; color: var(--color-neutral-500); }
.bar-group { display: flex; gap: 2px; height: 16px; }
.bar { height: 100%; border-radius: 2px; transition: width 300ms ease; }
.bar.income { background: var(--color-success-500); }
.bar.expense { background: var(--color-error-500); }
.amount { font-size: 0.8rem; font-weight: 600; font-family: var(--font-mono); text-align: right; }
.summary-footer { margin-top: var(--spacing-md); padding-top: var(--spacing-sm); border-top: 1px solid var(--color-neutral-100); font-size: 0.85rem; color: var(--color-neutral-600); }
.summary-footer strong { color: var(--color-success-600); }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>

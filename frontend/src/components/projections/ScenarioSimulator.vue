<template>
  <div class="scenario-section">
    <div class="card">
      <h3>¿Qué pasaría si...?</h3>
      <form class="scenario-form" @submit.prevent="$emit('run')">
        <div class="form-row">
          <div class="form-group">
            <label>Cambio en ingresos (%)</label>
            <input v-model.number="localForm.income_change" type="number" step="0.1">
          </div>
          <div class="form-group">
            <label>Cambio en gastos (%)</label>
            <input v-model.number="localForm.expense_change" type="number" step="0.1">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Pago extra de deuda</label>
            <input v-model.number="localForm.extra_debt" type="number" step="1000" min="0">
          </div>
          <div class="form-group">
            <label>Ahorro mensual nuevo</label>
            <input v-model.number="localForm.new_savings" type="number" step="1000" min="0">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Meses a proyectar</label>
            <input v-model.number="localForm.months" type="number" min="1" max="60">
          </div>
          <div class="form-group">
            <button type="submit" class="btn-primary" :disabled="loading">
              {{ loading ? 'Calculando...' : 'Simular' }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <div v-if="result" class="card">
      <h3>Resultado</h3>
      <div class="scenario-summary">
        <div><span class="label">Deuda libre en</span><span class="value">{{ result.debt_free_date || 'N/A' }}</span></div>
        <div><span class="label">Patrimonio proyectado</span><span class="value income">${{ fmt(result.projected_net_worth) }}</span></div>
        <div><span class="label">Ahorro proyectado</span><span class="value income">${{ fmt(result.projected_savings) }}</span></div>
      </div>
      <div v-if="result.projections?.length" class="chart-container">
        <div v-for="p in result.projections" :key="p.month" class="projection-row">
          <span class="month-label">Mes {{ p.month }}</span>
          <div class="bar-group">
            <div class="bar income" :style="{ width: barWidth(p.income, maxVal) + '%' }" />
            <div class="bar expense" :style="{ width: barWidth(p.expenses, maxVal) + '%' }" />
            <div class="bar debt" :style="{ width: barWidth(p.debt_payment, maxVal) + '%' }" />
          </div>
          <span class="amount">${{ fmt(p.cumulative_savings) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  form: { type: Object, required: true },
  result: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  maxVal: { type: Number, default: 1 },
  barWidth: { type: Function, required: true },
})

const emit = defineEmits(['run', 'update:form'])

const localForm = ref({ ...props.form })

watch(
  localForm,
  (val) => {
    emit('update:form', { ...val })
  },
  { deep: true },
)
</script>

<style scoped>
.scenario-section { display: flex; flex-direction: column; gap: var(--spacing-md); }
.card h3 { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--spacing-md); }
.scenario-form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-primary-600);
  color: white; border: none; border-radius: var(--radius-md);
  font-size: 0.85rem; font-weight: 600; cursor: pointer; align-self: end;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
.scenario-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md); margin-bottom: var(--spacing-md); }
.scenario-summary > div { text-align: center; }
.label { display: block; font-size: 0.75rem; color: var(--color-neutral-500); margin-bottom: 2px; }
.value { display: block; font-size: 1rem; font-weight: 600; font-family: var(--font-mono); color: var(--color-neutral-900); }
.value.income { color: var(--color-success-600); }
.chart-container { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.projection-row { display: grid; grid-template-columns: 70px 1fr 80px; align-items: center; gap: var(--spacing-sm); }
.month-label { font-size: 0.75rem; color: var(--color-neutral-500); }
.bar-group { display: flex; gap: 2px; height: 16px; }
.bar { height: 100%; border-radius: 2px; transition: width 300ms ease; }
.bar.income { background: var(--color-success-500); }
.bar.expense { background: var(--color-error-500); }
.bar.debt { background: var(--color-warning-500); }
.amount { font-size: 0.8rem; font-weight: 600; font-family: var(--font-mono); text-align: right; }

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
  .scenario-summary { grid-template-columns: 1fr; }
}
</style>

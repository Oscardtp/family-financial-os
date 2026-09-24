<template>
  <div class="bcfg">
    <section class="bcfg-section" aria-labelledby="bcfg-month">
      <h4 id="bcfg-month" class="bcfg-section-title">Presupuesto mensual</h4>
      <div class="bcfg-kpi-row">
        <span class="bcfg-kpi-label">Mes activo</span>
        <strong class="bcfg-kpi-value">{{ monthLabel || '—' }}</strong>
      </div>
      <div class="bcfg-kpi-row">
        <span class="bcfg-kpi-label">Estado</span>
        <StatusBadge :label="status.label" :variant="status.variant" />
      </div>
      <div class="bcfg-kpi-row">
        <span class="bcfg-kpi-label">Última actualización</span>
        <span class="bcfg-kpi-text">{{ lastUpdated }}</span>
      </div>
    </section>

    <section class="bcfg-section" aria-labelledby="bcfg-income">
      <h4 id="bcfg-income" class="bcfg-section-title">Ingreso de referencia</h4>
      <div class="bcfg-form-row">
        <label class="bcfg-form-label" for="income-source">Origen</label>
        <select id="income-source" v-model="incomeSource" class="bcfg-select">
          <option
            v-for="s in incomeSources"
            :key="s.id"
            :value="s.id"
            :disabled="!!s.soon"
          >{{ s.label }}{{ s.soon ? ' (pronto)' : '' }}</option>
        </select>
      </div>
      <div class="bcfg-form-row">
        <label class="bcfg-form-label" for="income-amount">Monto mensual</label>
        <div class="bcfg-input-wrap">
          <span class="bcfg-prefix">$</span>
          <input
            id="income-amount"
            v-model="incomeAmount"
            type="number"
            class="bcfg-input"
            min="0"
            step="10000"
            placeholder="0"
          />
        </div>
      </div>
      <div v-if="incomeError" class="bcfg-error" role="alert" aria-live="assertive">{{ incomeError }}</div>
      <p v-if="incomeMsg" class="bcfg-ok" role="status">{{ incomeMsg }}</p>
      <div class="bcfg-row-btns">
        <button class="btn btn-primary" @click="save" :disabled="saving">
          {{ saving ? 'Guardando…' : 'Guardar configuración' }}
        </button>
      </div>
    </section>

    <section class="bcfg-section" aria-labelledby="bcfg-prefs">
      <h4 id="bcfg-prefs" class="bcfg-section-title">Preferencias</h4>
      <div class="bcfg-switch-row">
        <span class="bcfg-switch-label">Rollover mensual <em class="bcfg-soon">Pronto</em></span>
        <button
          type="button"
          role="switch"
          :aria-checked="prefRollover"
          class="bcfg-switch"
          :class="{ on: prefRollover }"
          @click="prefRollover = !prefRollover"
          aria-label="Rollover mensual"
        ><span class="bcfg-switch-knob" /></button>
      </div>
      <div class="bcfg-switch-row">
        <span class="bcfg-switch-label">Notificaciones de presupuesto <em class="bcfg-soon">Pronto</em></span>
        <button
          type="button"
          role="switch"
          :aria-checked="prefNotify"
          class="bcfg-switch"
          :class="{ on: prefNotify }"
          @click="prefNotify = !prefNotify"
          aria-label="Notificaciones de presupuesto"
        ><span class="bcfg-switch-knob" /></button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import StatusBadge from '@/components/StatusBadge.vue'

const props = defineProps({
  monthLabel: { type: String, default: '' },
  status: {
    type: Object,
    default: () => ({ label: 'Vamos bien', variant: 'success' }),
  },
  lastUpdated: { type: String, default: 'Aún no guardada' },
  saving: { type: Boolean, default: false },
})

const emit = defineEmits(['save'])

const incomeSource = ref('manual')
const incomeAmount = ref('')
const incomeMsg = ref('')
const incomeError = ref('')
const prefRollover = ref(false)
const prefNotify = ref(false)

const incomeSources = [
  { id: 'manual', label: 'Manual' },
  { id: 'avg_3m', label: 'Promedio 3 meses', soon: true },
  { id: 'recurring', label: 'Ingreso recurrente', soon: true },
  { id: 'dashboard', label: 'Dashboard mensual', soon: true },
]

function save() {
  incomeMsg.value = ''
  incomeError.value = ''
  if (incomeAmount.value !== '' && Number(incomeAmount.value) < 0) {
    incomeError.value = 'El monto no puede ser negativo.'
    return
  }
  emit('save', {
    source: incomeSource.value,
    amount: incomeAmount.value,
    prefRollover: prefRollover.value,
    prefNotify: prefNotify.value,
  })
  incomeMsg.value = 'Configuración guardada.'
}

function reset() {
  incomeSource.value = 'manual'
  incomeAmount.value = ''
  incomeMsg.value = ''
  incomeError.value = ''
  prefRollover.value = false
  prefNotify.value = false
}

defineExpose({ reset })
</script>

<style scoped>
.bcfg { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bcfg-section { display: flex; flex-direction: column; gap: var(--spacing-sm); padding-bottom: var(--spacing-md); border-bottom: 1px solid var(--color-neutral-100); }
.bcfg-section:last-child { border-bottom: none; padding-bottom: 0; }
.bcfg-section-title { font-size: 0.85rem; font-weight: 700; color: var(--color-neutral-800); margin: 0; }
.bcfg-kpi-row { display: flex; justify-content: space-between; align-items: baseline; gap: var(--spacing-md); }
.bcfg-kpi-label { font-size: 0.85rem; color: var(--color-neutral-500); }
.bcfg-kpi-value { font-family: var(--font-mono); font-size: 1rem; font-weight: 700; color: var(--color-neutral-900); }
.bcfg-kpi-text { font-size: 0.85rem; color: var(--color-neutral-700); }
.bcfg-form-row { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-50); }
.bcfg-form-row:last-child { border-bottom: none; }
.bcfg-form-label { font-size: 0.85rem; font-weight: 500; color: var(--color-neutral-700); min-width: 140px; }
.bcfg-input-wrap { display: flex; align-items: center; gap: 4px; }
.bcfg-prefix { font-size: 0.85rem; color: var(--color-neutral-400); font-family: var(--font-mono); }
.bcfg-input { width: 140px; padding: var(--spacing-sm); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); font-size: 0.85rem; font-family: var(--font-mono); text-align: right; transition: border-color var(--transition-fast); }
.bcfg-input:focus { outline: none; border-color: var(--color-primary-500); box-shadow: 0 0 0 3px var(--color-primary-100); }
.bcfg-input::-webkit-inner-spin-button, .bcfg-input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.bcfg-input[type=number] { -moz-appearance: textfield; }
.bcfg-select { padding: var(--spacing-xs) var(--spacing-sm); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); font-size: 0.85rem; background: var(--color-neutral-0); color: var(--color-neutral-800); min-height: 44px; }
.bcfg-select:focus { outline: none; border-color: var(--color-primary-500); box-shadow: 0 0 0 3px var(--color-primary-100); }
.bcfg-error { background: var(--color-error-50); color: var(--color-error-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: 0.85rem; }
.bcfg-ok { background: var(--color-success-50); color: var(--color-success-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: 0.85rem; margin: 0; }
.bcfg-row-btns { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.bcfg-switch-row { display: flex; justify-content: space-between; align-items: center; gap: var(--spacing-md); padding: var(--spacing-xs) 0; }
.bcfg-switch-label { font-size: 0.85rem; color: var(--color-neutral-700); }
.bcfg-soon { font-style: normal; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-neutral-400); background: var(--color-neutral-100); padding: 2px 8px; border-radius: 999px; margin-left: 6px; }
.bcfg-switch { width: 48px; height: 28px; border-radius: 999px; border: none; background: var(--color-neutral-200); cursor: pointer; position: relative; transition: background var(--transition-fast); flex-shrink: 0; }
.bcfg-switch::before { content: ''; position: absolute; inset: -8px; }
.bcfg-switch.on { background: var(--color-primary-600); }
.bcfg-switch:focus-visible { outline: 2px solid var(--color-primary-500); outline-offset: 2px; }
.bcfg-switch-knob { position: absolute; top: 3px; left: 3px; width: 22px; height: 22px; border-radius: 999px; background: var(--color-neutral-0); transition: left var(--transition-fast); box-shadow: var(--shadow-sm); }
.bcfg-switch.on .bcfg-switch-knob { left: 23px; }
.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: transform var(--transition-fast); }
.btn:active:not(:disabled) { transform: scale(0.97); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--color-primary-600); color: var(--color-neutral-0); }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
@media (prefers-reduced-motion: reduce) { .bcfg-switch-knob, .bcfg-switch { transition: none; } }
</style>
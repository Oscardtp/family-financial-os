<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')" @keydown.escape="$emit('close')" role="dialog" aria-modal="true" aria-label="Crear nueva meta">
    <div class="modal-content modal-wide" @click.stop>
      <h3 class="modal-title">Nueva meta</h3>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label" for="goal-name">¿Qué estás juntando?</label>
          <input id="goal-name" v-model="form.name" type="text" class="form-input" placeholder="Ej: Viaje, Fondo de emergencia, Nuevo carro" maxlength="100" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="goal-target">¿Cuánto necesitas?</label>
            <div class="modal-amount-input">
              <span class="modal-currency">$</span>
              <input
                id="goal-target"
                :value="displayTarget"
                @input="onTargetInput"
                @focus="onTargetFocus"
                class="modal-amount-field"
                placeholder="0"
                min="1"
              />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label" for="goal-monthly">¿Cuánto puedes ahorrar al mes?</label>
            <div class="modal-amount-input">
              <span class="modal-currency">$</span>
              <input
                id="goal-monthly"
                :value="displayMonthly"
                @input="onMonthlyInput"
                @focus="onMonthlyFocus"
                class="modal-amount-field"
                placeholder="0"
                min="0"
              />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="goal-date">¿Para cuándo?</label>
            <input id="goal-date" v-model="form.target_date" type="date" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label" for="goal-type">Tipo</label>
            <select id="goal-type" v-model="form.goal_type" class="form-input">
              <option value="savings">Ahorro</option>
              <option value="investment">Inversión</option>
            </select>
          </div>
        </div>
        <div v-if="form.goal_type === 'investment'" class="form-row">
          <div class="form-group">
            <label class="form-label" for="goal-return">Rendimiento esperado (% EA)</label>
            <input id="goal-return" v-model="form.expected_return_rate" type="number" class="form-input" placeholder="Ej: 9" min="0" step="0.1" />
          </div>
          <div class="form-group">
            <label class="form-label" for="goal-horizon">Horizonte (meses)</label>
            <input id="goal-horizon" v-model="form.horizon_months" type="number" class="form-input" placeholder="Ej: 24" min="1" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label" for="goal-priority">Prioridad</label>
          <select id="goal-priority" v-model="form.priority" class="form-input">
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
          </select>
        </div>
        <p v-if="smartSummary" class="smart-summary">{{ smartSummary }}</p>
      </div>
      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
        <button
          class="btn-confirm"
          @click="handleSubmit"
          :disabled="!form.name || !fmtTarget.rawValue.value || submitting"
        >
          {{ submitting ? 'Creando...' : 'Crear meta' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useSmartCalculator } from '@/composables/useSmartCalculator'

const props = defineProps({
  show: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])

const { calcSmartFields } = useSmartCalculator()

const form = reactive({
  name: '',
  target_amount: '',
  monthly_contribution: '',
  target_date: '',
  goal_type: 'savings',
  expected_return_rate: '',
  horizon_months: '',
  priority: 'medium',
})

let fmtTarget = useFormattedNumber(0, { prefix: '' })
const displayTarget = computed(() => fmtTarget.displayValue.value)
const onTargetInput = (event) => fmtTarget.onInput(event)
const onTargetFocus = (event) => fmtTarget.onFocus(event)

let fmtMonthly = useFormattedNumber(0, { prefix: '' })
const displayMonthly = computed(() => fmtMonthly.displayValue.value)
const onMonthlyInput = (event) => fmtMonthly.onInput(event)
const onMonthlyFocus = (event) => fmtMonthly.onFocus(event)

watch(
  () => form.target_date,
  () => {
    if (form.target_date && !fmtMonthly.rawValue.value && displayTarget.value !== '0') {
      const target = parseFloat(fmtTarget.rawValue.value) || 0
      if (target > 0) {
        const now = new Date()
        const targetDate = new Date(form.target_date + 'T00:00:00')
        const months = Math.max((targetDate.getFullYear() - now.getFullYear()) * 12 + (targetDate.getMonth() - now.getMonth()), 1)
        fmtMonthly.setInitial(Math.ceil(target / months))
      }
    }
  }
)

const smartResult = computed(() => {
  const target = parseFloat(fmtTarget.rawValue.value) || 0
  const monthly = parseFloat(fmtMonthly.rawValue.value) || 0
  if (target <= 0) return { monthly: false, date: false, summary: '' }
  return calcSmartFields(target, form.target_date, monthly, 0)
})

const smartSummary = computed(() => smartResult.value.summary || '')

function handleSubmit() {
  if (!form.name || !fmtTarget.rawValue.value) return
  emit('submit', {
    ...form,
    target_amount: fmtTarget.rawValue.value,
    monthly_contribution: fmtMonthly.rawValue.value || null,
  })
}
</script>

<style scoped>
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

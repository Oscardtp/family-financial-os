<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')" @keydown.escape="$emit('close')" role="dialog" aria-modal="true" aria-label="Crear nueva meta">
    <FocusTrap :visible="show">
      <div class="modal-content modal-wide" @click.stop>
        <h3 class="modal-title">Nueva meta</h3>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label" for="goal-name">¿Qué estás juntando?</label>
            <input id="goal-name" v-model="form.name" type="text" class="form-input" name="name" placeholder="Ej: Viaje, Fondo de emergencia, Nuevo carro" maxlength="100" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="goal-target">¿Cuánto necesitas?</label>
              <div class="modal-amount-input">
                <span class="modal-currency">$</span>
                <input
                  id="goal-target"
                  name="target_amount"
                  :value="displayTarget"
                  @input="onTargetInput"
                  @focus="onTargetFocus"
                  class="modal-amount-field"
                  placeholder="0"
                  min="1"
                  inputmode="decimal"
                />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" for="goal-monthly">¿Cuánto puedes ahorrar al mes?</label>
              <div class="modal-amount-input">
                <span class="modal-currency">$</span>
                <input
                  id="goal-monthly"
                  name="monthly_contribution"
                  :value="displayMonthly"
                  @input="onMonthlyInput"
                  @focus="onMonthlyFocus"
                  class="modal-amount-field"
                  placeholder="0"
                  min="0"
                  inputmode="decimal"
                />
              </div>
            </div>
          </div>
          <div v-if="fechaObjetivoInfo" class="form-group goal-date-estimate">
            <label class="form-label">Fecha objetivo estimada</label>
            <div class="goal-date-display">
              <input
                type="text"
                class="goal-date-input"
                :value="fechaObjetivoInfo.fechaObjetivo"
                readonly
                aria-label="Fecha objetivo estimada"
              />
            </div>
          </div>
          <div v-if="fechaObjetivoInfo?.warning" class="modal-goal-date-warning">
            <AlertTriangle :size="16" aria-hidden="true" />
            <span>{{ fechaObjetivoInfo.warning }}</span>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="goal-date">¿Para cuándo?</label>
              <input id="goal-date" v-model="form.target_date" type="date" class="form-input" name="target_date" />
            </div>
            <div class="form-group">
              <label class="form-label" for="goal-type">Tipo</label>
              <select id="goal-type" v-model="form.goal_type" class="form-input" name="goal_type">
                <option value="savings">Ahorro</option>
                <option value="investment">Inversión</option>
              </select>
            </div>
          </div>
          <div v-if="form.goal_type === 'investment'" class="form-row">
            <div class="form-group">
              <label class="form-label" for="goal-return">Rendimiento esperado (% EA)</label>
              <input id="goal-return" v-model="form.expected_return_rate" type="number" class="form-input" name="expected_return_rate" placeholder="Ej: 9" min="0" step="0.1" inputmode="decimal" />
            </div>
            <div class="form-group">
              <label class="form-label" for="goal-horizon">Horizonte (meses)</label>
              <input id="goal-horizon" v-model="form.horizon_months" type="number" class="form-input" name="horizon_months" placeholder="Ej: 24" min="1" inputmode="numeric" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Prioridad</label>
            <div class="priority-segment">
              <button type="button" class="priority-btn" :class="{ active: form.priority === 'low' }" @click="form.priority = 'low'">Baja</button>
              <button type="button" class="priority-btn" :class="{ active: form.priority === 'medium' }" @click="form.priority = 'medium'">Media</button>
              <button type="button" class="priority-btn" :class="{ active: form.priority === 'high' }" @click="form.priority = 'high'">Alta</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label" for="goal-description">Nota rápida</label>
            <input id="goal-description" v-model="form.description" type="text" class="form-input" name="description" placeholder="Si quieres agregar algo..." maxlength="255" />
          </div>
          <p v-if="smartSummary" class="smart-summary">{{ smartSummary }}</p>
        </div>
        <div class="modal-actions symmetric">
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
    </FocusTrap>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Calendar, AlertTriangle } from 'lucide-vue-next'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useSmartCalculator } from '@/composables/useSmartCalculator'
import { calcularFechaObjetivo } from '@/composables/useGoalDate'
import FocusTrap from '@/components/FocusTrap.vue'

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
  description: '',
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

const fechaObjetivoInfo = computed(() => calcularFechaObjetivo(fmtTarget.rawValue.value, fmtMonthly.rawValue.value))

function handleSubmit() {
  if (!form.name || !fmtTarget.rawValue.value) return
  emit('submit', {
    ...form,
    target_amount: fmtTarget.rawValue.value,
    monthly_contribution: fmtMonthly.rawValue.value || null,
    description: form.description || null,
  })
}
</script>

<style scoped>
.modal-content.modal-wide {
  max-height: 90vh;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  max-width: 560px;
}

.modal-title {
  text-align: center;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.modal-amount-input {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  transition: border-color var(--transition-fast);
  min-height: 44px;
  min-width: 0;
}

.modal-amount-input.error {
  border-color: var(--color-error-500);
}

.modal-currency {
  font-size: 18px;
  color: var(--color-neutral-400);
  flex-shrink: 0;
}

.modal-amount-field {
  flex: 1;
  border: none;
  font-size: 18px;
  font-weight: 700;
  outline: none;
  background: transparent;
  font-family: var(--font-mono);
  min-height: 44px;
  min-width: 0;
}

.priority-segment {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.priority-btn {
  padding: 10px 0;
  border: 1.5px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
  color: var(--color-neutral-700);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.priority-btn.active {
  border-color: var(--color-primary-500);
  background: var(--color-primary-50);
  color: var(--color-primary-700);
  font-weight: 600;
}

.modal-actions.symmetric {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: var(--spacing-md);
}

.modal-actions.symmetric .btn-cancel {
  justify-content: center;
}

.smart-summary {
  margin: var(--spacing-sm) 0 0;
  font-size: 0.8rem;
  color: var(--color-primary-600);
  text-align: center;
}

.goal-date-estimate {
  margin-bottom: var(--spacing-sm);
}

.goal-date-display {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  background: var(--color-neutral-50);
  min-height: 44px;
}

.goal-date-display:focus-within {
  box-shadow: 0 0 0 3px rgba(47, 113, 229, 0.12);
}

.goal-date-input {
  width: 100%;
  border: none;
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
  background: transparent;
  color: var(--color-neutral-600);
  outline: none;
}

.modal-goal-date-warning {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-warning-50);
  border: 1px solid var(--color-warning-100);
  border-radius: var(--radius-md);
  color: var(--color-error-600);
  font-size: 0.8rem;
  line-height: 1.4;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content.modal-wide {
    width: 100%;
    max-width: 100%;
    padding: var(--spacing-md);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  }

  .modal-actions.symmetric {
    grid-template-columns: 1fr;
  }
}
</style>

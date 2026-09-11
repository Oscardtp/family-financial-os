<template>
  <form class="goal-form" @submit.prevent="handleSubmit">
    <div class="form-field">
      <label class="form-question">¿Para qué estás ahorrando?</label>
      <input
        ref="nameRef"
        v-model="name"
        type="text"
        class="text-input"
        placeholder="Viaje, carro, emergencia..."
        id="quick-goal-name"
        name="name"
      >
      <span v-if="submitted && !name" class="field-error">¿Para qué es?</span>
    </div>

    <div class="form-field">
      <label class="form-question">¿Cuánto necesitas?</label>
      <div class="amount-input" :class="{ error: submitted && !amount }">
        <span class="currency">$</span>
        <input
          ref="amountRef"
          :value="displayAmount"
          @input="onAmountInput"
          @focus="onAmountFocus"
          class="amount-field"
          placeholder="Ej: 2.000.000"
          aria-label="Monto objetivo"
          id="quick-goal-amount"
          name="amount"
        >
      </div>
      <span v-if="submitted && !amount" class="field-error">¿Cuánto necesitas?</span>
    </div>

    <div class="form-field">
      <label class="form-question">¿Cuánto puedes guardar cada mes?</label>
      <div class="amount-input">
        <span class="currency">$</span>
        <input
          :value="displayContribution"
          @input="onContributionInput"
          @focus="onContributionFocus"
          class="amount-field"
          placeholder="0"
          aria-label="Ahorro mensual"
          id="quick-goal-contribution"
          name="monthly_contribution"
        >
      </div>
    </div>

    <div v-if="fechaObjetivoInfo" class="form-field">
      <label class="form-question">Fecha objetivo estimada</label>
      <div class="fecha-objetivo-display">
        <input
          type="text"
          class="fecha-objetivo-input"
          :value="fechaObjetivoInfo.fechaObjetivo"
          readonly
          aria-label="Fecha objetivo estimada"
        >
      </div>
    </div>
    <div v-if="fechaObjetivoInfo?.warning" class="form-field">
      <div class="goal-date-warning">
        <AlertTriangle :size="16" aria-hidden="true" />
        <span>{{ fechaObjetivoInfo.warning }}</span>
      </div>
    </div>

    <div class="form-field">
      <label class="form-question">¿Para cuándo?</label>
      <input v-model="targetDate" type="date" class="date-input" aria-label="Fecha objetivo" id="quick-goal-date" name="target_date">
    </div>

    <div class="form-field">
      <label class="form-question">¿Qué tipo de meta es?</label>
      <select v-model="goalType" class="form-select" aria-label="Tipo de meta" id="quick-goal-type" name="goal_type">
        <option value="savings">Ahorro</option>
        <option value="investment">Inversión</option>
      </select>
    </div>

    <div v-if="goalType === 'investment'" class="form-row">
      <div class="form-field">
        <label class="form-question">Rendimiento esperado (% EA)</label>
        <input
          v-model="expectedReturnRate"
          type="number"
          class="text-input"
          placeholder="Ej: 9"
          min="0"
          step="0.1"
          id="quick-goal-return"
          name="expected_return_rate"
        >
      </div>
      <div class="form-field">
        <label class="form-question">Horizonte (meses)</label>
        <input
          v-model="horizonMonths"
          type="number"
          class="text-input"
          placeholder="Ej: 24"
          min="1"
          id="quick-goal-horizon"
          name="horizon_months"
        >
      </div>
    </div>

    <div v-if="smartSummary" class="smart-summary">
      <Calculator :size="16" />
      <span>{{ smartSummary }}</span>
    </div>

    <div class="form-field">
      <input
        v-model="description"
        type="text"
        class="text-input"
        placeholder="Nota rápida (si quieres)"
        id="quick-goal-description"
        name="description"
      >
    </div>

    <button type="submit" class="submit-btn" :disabled="loading" aria-label="Empezar a ahorrar">
      <span v-if="loading" class="spinner"></span>
      {{ loading ? 'Creando...' : 'Empezar a ahorrar' }}
    </button>
  </form>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { Calculator, Calendar, AlertTriangle } from 'lucide-vue-next'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useSmartCalculator } from '@/composables/useSmartCalculator'
import { calcularFechaObjetivo } from '@/composables/useGoalDate'

const props = defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const nameRef = ref(null)
const amountRef = ref(null)
const submitted = ref(false)
const name = ref('')
const description = ref('')
const monthlyContribution = ref(0)
const targetDate = ref('')
const goalType = ref('savings')
const expectedReturnRate = ref('')
const horizonMonths = ref('')

let fmt = useFormattedNumber(0, { prefix: '' })
const amount = computed(() => fmt.rawValue.value)
const displayAmount = computed(() => fmt.displayValue.value)

const onAmountInput = (event) => fmt.onInput(event)
const onAmountFocus = (event) => fmt.onFocus(event)

let fmtContrib = useFormattedNumber(0, { prefix: '' })
const displayContribution = computed(() => fmtContrib.displayValue.value)

const onContributionInput = (event) => {
  fmtContrib.onInput(event)
  monthlyContribution.value = fmtContrib.rawValue.value
}
const onContributionFocus = (event) => fmtContrib.onFocus(event)

const { calcSmartFields } = useSmartCalculator()

const smartResult = ref({ monthly: false, date: false, summary: '' })

const smartSummary = computed(() => smartResult.value.summary || '')

const fechaObjetivoInfo = computed(() => calcularFechaObjetivo(amount.value, monthlyContribution.value))

watch([amount, targetDate, monthlyContribution], () => {
  if (amount.value > 0) {
    smartResult.value = calcSmartFields(amount.value, targetDate.value, monthlyContribution.value, 0)
    if (smartResult.value.monthly && !monthlyContribution.value) {
      const calc = Math.ceil(amount.value / Math.max(1, monthsUntil(targetDate.value)))
      monthlyContribution.value = calc
    }
  }
}, { immediate: true })

function monthsUntil(date) {
  if (!date) return 0
  const now = new Date()
  const target = new Date(date + 'T00:00:00')
  return Math.max((target.getFullYear() - now.getFullYear()) * 12 + (target.getMonth() - now.getMonth()), 1)
}

onMounted(() => nextTick(() => nameRef.value?.focus()))

function handleSubmit() {
  submitted.value = true
  if (!name.value || !amount.value) return

  const payload = {
    name: name.value,
    target_amount: amount.value,
    monthly_contribution: monthlyContribution.value || null,
    target_date: targetDate.value || null,
    goal_type: goalType.value,
    description: description.value || null,
  }

  if (goalType.value === 'investment') {
    payload.expected_return_rate = expectedReturnRate.value ? parseFloat(expectedReturnRate.value) : null
    payload.horizon_months = horizonMonths.value ? parseInt(horizonMonths.value) : null
  }

  emit('submit', payload)
}
</script>

<style scoped>
.form-field { margin-bottom: var(--spacing-lg); }

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-question {
  display: block;
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-neutral-700);
  margin-bottom: var(--spacing-sm);
}

.amount-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  transition: border-color var(--transition-fast);
  min-height: 44px;
}
.amount-input.error { border-color: var(--color-error-400); }

.currency { font-size: var(--font-size-xl); color: var(--color-neutral-400); }

.amount-field {
  flex: 1;
  border: none;
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-neutral-900);
  outline: none;
  width: 100%;
  background: transparent;
}

.amount-field::placeholder { color: var(--color-neutral-300); }

.date-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
  min-height: 44px;
}

.form-select {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
  background: var(--color-neutral-0);
  transition: border-color var(--transition-fast);
  min-height: 44px;
}

.text-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
  min-height: 44px;
}

.field-error {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-error-500);
  margin-top: var(--spacing-xs);
}

.submit-btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: white;
  background: var(--color-info-500);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.submit-btn:hover:not(:disabled) { opacity: 0.9; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.smart-summary {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-surface-tinted-teal);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
  color: var(--color-success-700);
  line-height: 1.4;
}

.fecha-objetivo-display {
  display: flex;
  align-items: center;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  background: var(--color-neutral-50);
  min-height: 44px;
}

.fecha-objetivo-display:focus-within {
  box-shadow: 0 0 0 3px rgba(47, 113, 229, 0.12);
}

.fecha-objetivo-input {
  width: 100%;
  border: none;
  font-size: var(--font-size-sm);
  font-family: var(--font-sans);
  background: transparent;
  color: var(--color-neutral-600);
  outline: none;
}

.goal-date-warning {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-warning-50);
  border: 1px solid var(--color-warning-100);
  border-radius: var(--radius-md);
  color: var(--color-error-600);
  font-size: var(--font-size-sm);
  line-height: 1.4;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

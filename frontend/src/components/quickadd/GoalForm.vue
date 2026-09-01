<template>
  <form class="goal-form" @submit.prevent="handleSubmit">
    <div class="form-field">
      <label class="form-question">¿Qué meta quieres?</label>
      <input
        ref="nameRef"
        v-model="name"
        type="text"
        class="text-input"
        placeholder="Ej: Fondo de emergencia, Vacaciones..."
      >
      <span v-if="submitted && !name" class="field-error">Debes indicar un nombre</span>
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
          placeholder="0"
        >
      </div>
      <span v-if="submitted && !amount" class="field-error">Debes indicar un monto objetivo</span>
    </div>

    <div class="form-field">
      <label class="form-question">¿Cuánto puedes guardar al mes?</label>
      <div class="amount-input-small">
        <span class="currency-small">$</span>
        <input
          v-model.number="monthlyContribution"
          type="number"
          class="amount-field-small"
          placeholder="0"
          min="1"
        >
      </div>
    </div>

    <div class="form-field">
      <label class="form-question">¿Para cuándo?</label>
      <input v-model="targetDate" type="date" class="date-input">
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
        placeholder="¿Algo más? (opcional)"
      >
    </div>

    <button type="submit" class="submit-btn" :disabled="loading">
      <span v-if="loading" class="spinner"></span>
      {{ loading ? 'Creando...' : 'Crear meta' }}
    </button>
  </form>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { Calculator } from 'lucide-vue-next'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useSmartCalculator } from '@/composables/useSmartCalculator'

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

let fmt = useFormattedNumber(0, { prefix: '$' })
const amount = computed(() => fmt.rawValue.value)
const displayAmount = computed(() => fmt.displayValue.value)

const onAmountInput = (event) => fmt.onInput(event)
const onAmountFocus = (event) => fmt.onFocus(event)

const { calcSmartFields } = useSmartCalculator()

const smartResult = ref({ monthly: false, date: false, summary: '' })

const smartSummary = computed(() => smartResult.value.summary || '')

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

  emit('submit', {
    name: name.value,
    target_amount: amount.value,
    monthly_contribution: monthlyContribution.value || null,
    target_date: targetDate.value || null,
  })
}
</script>

<style scoped>
.form-field { margin-bottom: var(--spacing-lg); }

.form-question {
  display: block;
  font-size: 15px;
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
}

.amount-input:focus-within { border-color: var(--color-primary-500); }
.amount-input.error { border-color: var(--color-error-400); }

.currency { font-size: 24px; color: var(--color-neutral-400); }

.amount-field {
  flex: 1;
  border: none;
  font-size: 32px;
  font-weight: 700;
  color: var(--color-neutral-900);
  outline: none;
  width: 100%;
  background: transparent;
}

.amount-field::placeholder { color: var(--color-neutral-300); }

.amount-input-small {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
}

.amount-input-small:focus-within { border-color: var(--color-primary-500); }

.currency-small { font-size: 16px; color: var(--color-neutral-400); }

.amount-field-small {
  flex: 1;
  border: none;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-neutral-900);
  outline: none;
  width: 100%;
  background: transparent;
}

.date-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--color-neutral-700);
}

.date-input:focus { border-color: var(--color-primary-500); outline: none; }

.text-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--color-neutral-700);
}

.text-input:focus { border-color: var(--color-primary-500); outline: none; }

.field-error {
  display: block;
  font-size: 12px;
  color: var(--color-error-500);
  margin-top: var(--spacing-xs);
}

.submit-btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
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
  font-size: 13px;
  color: var(--color-success-700);
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
</style>

<template>
  <form class="recurring-form" @submit.prevent="handleSubmit">
    <div class="form-field">
      <label class="form-question">¿Cuánto es al mes?</label>
      <div class="amount-input" :class="{ error: submitted && !amount }">
        <span class="currency">$</span>
        <input
          ref="amountRef"
          :value="displayAmount"
          @input="onAmountInput"
          @focus="onAmountFocus"
          class="amount-field"
          placeholder="Ej: 55.000"
          aria-label="Monto mensual"
        >
      </div>
      <span v-if="submitted && !amount" class="field-error">¿Cuánto es?</span>
    </div>

    <div class="form-field">
      <label class="form-question">¿Qué pago es?</label>
      <input
        v-model="name"
        type="text"
        class="text-input"
        placeholder="Netflix, arriendo, celular..."
      >
      <span v-if="submitted && !name" class="field-error">¿Cómo se llama ese pago?</span>
    </div>

    <div class="form-field">
      <label class="form-question">¿Cada cuándo?</label>
      <div class="frequency-grid">
        <button
          type="button"
          class="freq-btn"
          :class="{ selected: frequency === 'monthly' }"
          @click="frequency = 'monthly'"
        >Mensual</button>
        <button
          type="button"
          class="freq-btn"
          :class="{ selected: frequency === 'weekly' }"
          @click="frequency = 'weekly'"
        >Semanal</button>
      </div>
    </div>

    <div class="form-field">
      <label class="form-question">¿El día qué?</label>
      <select v-model.number="dayOfMonth" class="form-select" aria-label="Día del pago">
        <option :value="0" disabled>Seleccionar día</option>
        <option v-for="d in 28" :key="d" :value="d">Día {{ d }}</option>
      </select>
      <span v-if="submitted && !dayOfMonth" class="field-error">¿El día qué?</span>
    </div>

    <div class="form-field">
      <input
        v-model="description"
        type="text"
        class="text-input"
        placeholder="Nota rápida (si quieres)"
      >
    </div>

    <button type="submit" class="submit-btn" :disabled="loading" aria-label="Activar pago fijo">
      <span v-if="loading" class="spinner"></span>
      {{ loading ? 'Activando...' : 'Activar pago fijo' }}
    </button>
  </form>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'

const props = defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const amountRef = ref(null)
const submitted = ref(false)
const name = ref('')
const description = ref('')
const frequency = ref('monthly')
const dayOfMonth = ref(new Date().getDate() > 28 ? 28 : new Date().getDate())

let fmt = useFormattedNumber(0, { prefix: '' })
const amount = computed(() => fmt.rawValue.value)
const displayAmount = computed(() => fmt.displayValue.value)

const onAmountInput = (event) => fmt.onInput(event)
const onAmountFocus = (event) => fmt.onFocus(event)

onMounted(() => nextTick(() => amountRef.value?.focus()))

function handleSubmit() {
  submitted.value = true
  if (!amount.value || !name.value || !dayOfMonth.value) return

  emit('submit', {
    amount: amount.value,
    name: name.value,
    frequency: frequency.value,
    day_of_month: dayOfMonth.value,
    description: description.value || null,
  })
}
</script>

<style scoped>
.form-field { margin-bottom: var(--spacing-lg); }

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
}

.amount-input:focus-within { border-color: var(--color-primary-500); }
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

.frequency-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
}

.freq-btn {
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-neutral-700);
  transition: all var(--transition-fast);
}

.freq-btn:hover { border-color: var(--color-primary-300); }
.freq-btn.selected { border-color: var(--color-primary-500); background: var(--color-primary-50); color: var(--color-primary-700); }

.form-select {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
  background: var(--color-neutral-0);
}

.form-select:focus { border-color: var(--color-primary-500); outline: none; }

.text-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
}

.text-input:focus { border-color: var(--color-primary-500); outline: none; }

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
  background: var(--color-warning-500);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.submit-btn:hover:not(:disabled) { opacity: 0.9; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

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

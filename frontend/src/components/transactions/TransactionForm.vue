<template>
  <div class="card form-card card-hover">
    <div class="type-tabs">
      <button type="button" class="type-tab" :class="{ active: form.type === 'expense', expense: form.type === 'expense' }" @click="form.type = 'expense'">
        💸 Gasto
      </button>
      <button type="button" class="type-tab" :class="{ active: form.type === 'income', income: form.type === 'income' }" @click="form.type = 'income'">
        💰 Ingreso
      </button>
    </div>

    <form class="form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label class="form-label">{{ form.type === 'expense' ? '¿Cuánto gastaste?' : '¿Cuánto recibiste?' }}</label>
        <div class="amount-input-wrapper">
          <span class="amount-prefix">$</span>
          <input :value="fmtAmount.displayValue.value" @input="fmtAmount.onInput" @focus="fmtAmount.onFocus" class="form-input amount-input" placeholder="0">
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">¿En qué?</label>
        <select v-model.number="form.category_id" class="form-select">
          <option :value="0">Seleccionar categoría</option>
          <optgroup v-if="form.type === 'expense'" label="Gastos">
            <option v-for="c in expenseCategories" :key="c.id" :value="c.id">{{ c.icon || '📦' }} {{ c.name }}</option>
          </optgroup>
          <optgroup v-else label="Ingresos">
            <option v-for="c in incomeCategories" :key="c.id" :value="c.id">{{ c.icon || '💰' }} {{ c.name }}</option>
          </optgroup>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">¿De dónde?</label>
        <select v-model.number="form.account_id" class="form-select">
          <option :value="0" disabled>Seleccionar cuenta</option>
          <option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.name }} (${{ fmt(a.balance) }})</option>
        </select>
      </div>

      <div class="optional-toggle">
        <button type="button" class="toggle-btn" @click="showOptional = !showOptional">
          {{ showOptional ? '▲' : '▼' }} Más opciones
        </button>
      </div>

      <div v-if="showOptional" class="optional-fields">
        <div class="form-group">
          <label class="form-label">Descripción (opcional)</label>
          <input v-model="form.description" class="form-input" type="text" placeholder="Qué fue?">
        </div>
        <div class="form-group">
          <label class="form-label">Fecha</label>
          <input v-model="form.date" class="form-input" type="date" required>
        </div>
      </div>

      <div class="form-actions">
        <span v-if="formError" class="form-error">{{ formError }}</span>
        <span v-if="successMessage" class="form-success">{{ successMessage }}</span>
        <button class="btn btn-primary" type="submit" :disabled="submitting">
          {{ submitting ? 'Guardando...' : submitButtonText }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  accounts: { type: Array, default: () => [] },
  incomeCategories: { type: Array, default: () => [] },
  expenseCategories: { type: Array, default: () => [] },
})

const emit = defineEmits(['submit'])

const submitting = ref(false)
const formError = ref('')
const successMessage = ref('')
const showOptional = ref(false)

let fmtAmount = useFormattedNumber(0, { prefix: '$' })

const form = reactive({
  account_id: 0,
  category_id: 0,
  type: 'expense',
  amount: 0,
  description: '',
  date: new Date().toISOString().split('T')[0],
})

const submitButtonText = computed(() => {
  if (submitting.value) return 'Guardando...'
  if (form.type === 'expense') return 'Guardar gasto'
  return 'Guardar ingreso'
})

watch(() => form.type, () => { form.category_id = 0 })

async function handleSubmit() {
  submitting.value = true
  formError.value = ''
  successMessage.value = ''

  const amount = fmtAmount.rawValue.value
  if (!amount || amount <= 0) {
    formError.value = 'Debes indicar un monto'
    submitting.value = false
    return
  }
  if (!form.account_id) {
    formError.value = 'Selecciona una cuenta'
    submitting.value = false
    return
  }

  try {
    await emit('submit', {
      account_id: form.account_id,
      category_id: form.category_id || undefined,
      type: form.type,
      amount,
      description: form.description || undefined,
      date: form.date,
    })
    successMessage.value = '¡Guardado!'
    setTimeout(() => { successMessage.value = '' }, 2000)
    form.account_id = props.accounts.length ? props.accounts[0].id : 0
    form.category_id = 0
    form.amount = 0
    form.description = ''
    form.date = new Date().toISOString().split('T')[0]
    fmtAmount = useFormattedNumber(0, { prefix: '$' })
  } catch (e) {
    formError.value = e?.response?.data?.detail || 'Error al crear la transacción'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.type-tabs { display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-lg); }
.type-tab {
  flex: 1; padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md);
  border: 2px solid var(--color-neutral-200); background: var(--color-neutral-0);
  font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 150ms ease;
}
.type-tab:hover { border-color: var(--color-neutral-300); }
.type-tab.active.expense { border-color: var(--color-error-500); background: var(--color-error-50); color: var(--color-error-700); }
.type-tab.active.income { border-color: var(--color-success-500); background: var(--color-success-50); color: var(--color-success-700); }
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-select {
  padding: var(--spacing-sm) var(--spacing-md); border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md); font-size: 0.875rem; outline: none;
}
.form-select:focus { border-color: var(--color-primary-400); }
.amount-input-wrapper { display: flex; align-items: center; }
.amount-prefix { font-size: 1.2rem; font-weight: 600; color: var(--color-neutral-400); margin-right: var(--spacing-xs); }
.amount-input { font-size: 1.5rem; font-weight: 700; font-family: var(--font-mono); }
.optional-toggle { text-align: center; }
.toggle-btn { background: none; border: none; color: var(--color-primary-600); font-size: 0.8rem; cursor: pointer; }
.optional-fields { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-actions { display: flex; align-items: center; justify-content: flex-end; gap: var(--spacing-md); }
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.form-success { color: var(--color-success-600); font-size: 0.8rem; margin-right: auto; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
</style>

<template>
  <div class="card">
    <h3 class="card-title">Nueva Meta</h3>
    <form class="form" @submit.prevent="handleSubmit">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Nombre</label>
          <input v-model="form.name" class="form-input" type="text" required placeholder="Nombre de la meta">
        </div>
        <div class="form-group">
          <label class="form-label">Prioridad</label>
          <select v-model="form.priority" class="form-select">
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Monto Objetivo</label>
          <div class="form-input-prefix">
            <span class="input-prefix">$</span>
            <input
              :value="fmtTarget.displayValue.value"
              @input="fmtTarget.onInput"
              class="form-input with-prefix"
              placeholder="0"
              required
            >
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Aporte Mensual</label>
          <div class="form-input-prefix">
            <span class="input-prefix">$</span>
            <input
              :value="fmtMonthly.displayValue.value"
              @input="fmtMonthly.onInput; userEditedMonthly = true"
              class="form-input with-prefix"
              placeholder="0"
            >
          </div>
          <span v-if="calcResult.monthly" class="form-hint">Calculado automáticamente</span>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Fecha Objetivo</label>
          <input v-model="form.target_date" class="form-input" type="date" @input="userEditedDate = true">
          <span v-if="calcResult.date" class="form-hint">Calculada automáticamente</span>
        </div>
        <div class="form-group">
          <label class="form-label">&nbsp;</label>
        </div>
      </div>
      <div v-if="calcResult.summary" class="calc-summary">
        {{ calcResult.summary }}
      </div>
      <div class="form-actions">
        <span v-if="formError" class="form-error">{{ formError }}</span>
        <button class="btn btn-primary" type="submit" :disabled="submitting">
          {{ submitting ? 'Creando...' : 'Crear Meta' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useSmartCalculator } from '@/composables/useSmartCalculator'

const { calcSmartFields } = useSmartCalculator()

const emit = defineEmits(['created'])

const submitting = ref(false)
const formError = ref('')
const userEditedMonthly = ref(false)
const userEditedDate = ref(false)

const form = reactive({
  name: '',
  target_amount: 0,
  target_date: '',
  monthly_contribution: 0,
  priority: 'medium',
})

const fmtTarget = useFormattedNumber(0, { prefix: '$' })
const fmtMonthly = useFormattedNumber(0, { prefix: '$' })

const calcResult = computed(() =>
  calcSmartFields(form.target_amount, form.target_date, form.monthly_contribution, 0)
)

let _debounce = false
watch(
  () => [form.target_amount, form.target_date, form.monthly_contribution],
  ([targetAmount, targetDate, monthlyContribution]) => {
    if (_debounce) return
    const remaining = Math.max(targetAmount || 0, 0)
    if (remaining <= 0) return
    const hasDate = !!targetDate
    const hasMonthly = monthlyContribution > 0

    if (hasDate && !hasMonthly && !userEditedMonthly.value) {
      const calc = Math.ceil(remaining / Math.max((new Date(targetDate + 'T00:00:00').getMonth() - new Date().getMonth() + (new Date(targetDate + 'T00:00:00').getFullYear() - new Date().getFullYear()) * 12), 1))
      if (calc !== monthlyContribution) {
        _debounce = true
        form.monthly_contribution = calc
        fmtMonthly.setInitial(calc)
        _debounce = false
      }
    } else if (hasMonthly && !hasDate && !userEditedDate.value) {
      const months = Math.ceil(remaining / monthlyContribution)
      const target = new Date()
      target.setMonth(target.getMonth() + months)
      const calc = target.toISOString().split('T')[0]
      if (calc && calc !== targetDate) {
        _debounce = true
        form.target_date = calc
        _debounce = false
      }
    }
  }
)

watch(() => form.target_amount, (val) => fmtTarget.setInitial(val))
watch(() => form.monthly_contribution, (val) => fmtMonthly.setInitial(val))
watch(() => fmtTarget.rawValue.value, (val) => { form.target_amount = val })
watch(() => fmtMonthly.rawValue.value, (val) => { form.monthly_contribution = val })

async function handleSubmit() {
  submitting.value = true
  formError.value = ''
  try {
    const { default: api } = await import('@/services/api')
    const payload = {
      name: form.name,
      target_amount: fmtTarget.rawValue.value,
      priority: form.priority,
    }
    if (form.target_date) payload.target_date = form.target_date
    if (fmtMonthly.rawValue.value > 0) payload.monthly_contribution = fmtMonthly.rawValue.value
    await api.post('/savings/goals', payload)
    emit('created')
    form.name = ''
    form.target_amount = 0
    form.target_date = ''
    form.monthly_contribution = 0
    form.priority = 'medium'
    fmtTarget.setInitial(0)
    fmtMonthly.setInitial(0)
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Error al crear la meta'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: var(--spacing-md);
}
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.form-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  outline: none;
  transition: border-color var(--transition-fast);
}
.form-select:focus { border-color: var(--color-primary-400); }
.form-input-prefix {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
  transition: border-color var(--transition-fast);
}
.form-input-prefix:focus-within { border-color: var(--color-primary-400); }
.input-prefix {
  padding: 0 var(--spacing-sm) 0 var(--spacing-md);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-neutral-400);
}
.form-input.with-prefix {
  border: none;
  background: transparent;
  padding-left: 0;
  flex: 1;
}
.form-input.with-prefix:focus { outline: none; }
.form-hint {
  font-size: 0.7rem;
  color: var(--color-primary-500);
  font-style: italic;
}
.calc-summary {
  background: var(--color-primary-50);
  border: 1px solid var(--color-primary-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: 0.8rem;
  color: var(--color-primary-700);
}
.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>

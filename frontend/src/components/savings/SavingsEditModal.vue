<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')" @keydown.escape="$emit('close')" role="dialog" aria-modal="true" :aria-label="`Editar ${goal?.name}`">
    <div class="modal" @click.stop>
      <h3 class="modal-title">Editar — {{ goal?.name }}</h3>
      <form class="form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">Nombre</label>
          <input v-model="form.name" class="form-input" type="text" required>
        </div>
        <div class="form-group">
          <label class="form-label">Monto Objetivo</label>
          <div class="form-input-prefix">
            <span class="input-prefix">$</span>
            <input
              :value="fmtTarget.displayValue.value"
              @input="fmtTarget.onInput"
              class="form-input with-prefix"
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
        <div class="form-group">
          <label class="form-label">Fecha Objetivo</label>
          <input v-model="form.target_date" class="form-input" type="date" @input="userEditedDate = true">
          <span v-if="calcResult.date" class="form-hint">Calculada automáticamente</span>
        </div>
        <div class="form-group">
          <label class="form-label">Prioridad</label>
          <select v-model="form.priority" class="form-select">
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
          </select>
        </div>
        <div v-if="calcResult.summary" class="calc-summary">
          {{ calcResult.summary }}
        </div>
        <div class="form-actions">
          <span v-if="error" class="form-error">{{ error }}</span>
          <button class="btn btn-sm" type="button" @click="$emit('close')">Cancelar</button>
          <button class="btn btn-primary" type="submit" :disabled="saving">
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useSmartCalculator } from '@/composables/useSmartCalculator'

const { calcSmartFields } = useSmartCalculator()

const props = defineProps({
  show: { type: Boolean, default: false },
  goal: { type: Object, default: null },
})

const emit = defineEmits(['close', 'saved'])

const saving = ref(false)
const error = ref('')
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

watch(() => props.goal, (g) => {
  if (g) {
    form.name = g.name
    form.target_amount = g.target_amount
    form.target_date = g.target_date || ''
    form.monthly_contribution = g.monthly_contribution || 0
    form.priority = g.priority
    fmtTarget.setInitial(g.target_amount)
    fmtMonthly.setInitial(g.monthly_contribution || 0)
    userEditedMonthly.value = false
    userEditedDate.value = false
  }
})

const calcResult = computed(() =>
  calcSmartFields(form.target_amount, form.target_date, form.monthly_contribution, props.goal?.current_amount || 0)
)

let _debounce = false
watch(
  () => [form.target_amount, form.target_date, form.monthly_contribution],
  ([targetAmount, targetDate, monthlyContribution]) => {
    if (_debounce) return
    const currentAmount = props.goal?.current_amount || 0
    const remaining = Math.max((targetAmount || 0) - currentAmount, 0)
    if (remaining <= 0) return
    const hasDate = !!targetDate
    const hasMonthly = monthlyContribution > 0

    if (hasDate && !hasMonthly && !userEditedMonthly.value) {
      const months = Math.max((new Date(targetDate + 'T00:00:00').getMonth() - new Date().getMonth() + (new Date(targetDate + 'T00:00:00').getFullYear() - new Date().getFullYear()) * 12), 1)
      const calc = Math.ceil(remaining / months)
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

async function handleSubmit() {
  saving.value = true
  error.value = ''
  try {
    const { default: api } = await import('@/services/api')
    const payload = {
      name: form.name,
      target_amount: fmtTarget.rawValue.value,
      priority: form.priority,
    }
    if (form.target_date) payload.target_date = form.target_date
    if (fmtMonthly.rawValue.value > 0) payload.monthly_contribution = fmtMonthly.rawValue.value
    else payload.monthly_contribution = null
    await api.put(`/savings/goals/${props.goal.id}`, payload)
    emit('saved')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'No pudimos actualizar la meta. Revisa los datos e inténtalo de nuevo.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  width: 420px;
  max-width: 90vw;
  box-shadow: var(--shadow-xl);
}
.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: var(--spacing-lg);
}
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  outline: none;
}
.form-select:focus { border-color: var(--color-primary-400); }
.form-input-prefix {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
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
.btn-sm { font-size: 0.8rem; background: var(--color-neutral-100); color: var(--color-neutral-700); }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
</style>

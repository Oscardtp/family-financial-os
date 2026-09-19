<template>
  <transition name="fade">
    <div v-if="open" class="modal-backdrop" @click.self="emit('close')">
      <div class="modal-content" role="dialog" aria-modal="true" aria-label="Editar pago recurrente">
        <div class="modal-handle" />
        <div class="modal-header">
          <h3 class="modal-title">{{ isEdit ? 'Editar' : 'Crear' }} pago recurrente</h3>
          <button class="btn-icon" @click="emit('close')" aria-label="Cerrar">
            <X :size="20" />
          </button>
        </div>

        <form class="edit-form" @submit.prevent="handleSubmit">
          <div class="form-field">
            <label class="form-label">¿Qué pago es?</label>
            <input
              v-model="form.name"
              type="text"
              class="text-input"
              placeholder="Netflix, arriendo, celular..."
              id="recurring-name-edit"
              name="name"
            >
          </div>

          <div class="form-field">
            <label class="form-label">¿Cuánto cuesta?</label>
            <div class="amount-input" :class="{ error: submitted && !form.amount }">
              <span class="currency">$</span>
              <input
                v-model.number="form.amount"
                type="number"
                class="amount-field"
                placeholder="Ej: 55000"
                id="recurring-amount-edit"
                name="amount"
                min="1"
              >
            </div>
            <span v-if="submitted && !form.amount" class="field-error">¿Cuánto es?</span>
          </div>

          <div class="form-field">
            <label class="form-label">Tipo</label>
            <div class="type-grid">
              <button
                type="button"
                class="type-btn"
                :class="{ selected: form.type === 'expense' }"
                @click="form.type = 'expense'"
              >Gasto</button>
              <button
                type="button"
                class="type-btn"
                :class="{ selected: form.type === 'income' }"
                @click="form.type = 'income'"
              >Ingreso</button>
            </div>
          </div>

          <div class="form-field">
            <label class="form-label">Frecuencia</label>
            <select v-model="form.frequency" class="form-select" id="recurring-freq-edit" name="frequency">
              <option v-for="opt in frequencyOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <div class="form-field">
            <label class="form-label">Día del mes</label>
            <select v-model.number="form.day_of_month" class="form-select" id="recurring-day-edit" name="day_of_month">
              <option :value="0" disabled>Seleccionar día</option>
              <option v-for="d in 28" :key="d" :value="d">Día {{ d }}</option>
            </select>
          </div>

          <div class="form-field">
            <label class="form-label">Próxima fecha de pago</label>
            <input
              v-model="form.next_due_date"
              type="date"
              class="text-input"
              id="recurring-due-edit"
              name="next_due_date"
            >
          </div>

          <div class="form-field">
            <label class="form-label">Descripción (opcional)</label>
            <input
              v-model="form.description"
              type="text"
              class="text-input"
              placeholder="Nota rápida..."
              id="recurring-desc-edit"
              name="description"
            >
          </div>

          <div class="form-field">
            <label class="form-check-row">
              <input type="checkbox" v-model="form.is_active" id="recurring-active-edit" name="is_active" />
              <span class="check-label">Activo</span>
            </label>
          </div>

          <button type="submit" class="submit-btn" :disabled="submitting">
            <span v-if="submitting" class="spinner" />
            {{ isEdit ? 'Guardar cambios' : 'Crear pago recurrente' }}
          </button>
        </form>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { useRecurringPayments } from '@/composables/useRecurringPayments'

const props = defineProps({
  open: { type: Boolean, default: false },
  payment: { type: Object, default: () => null },
})

const emit = defineEmits(['close', 'save'])

const { frequencyOptions } = useRecurringPayments()
const submitted = ref(false)
const submitting = ref(false)

const form = ref({
  name: '',
  amount: null,
  type: 'expense',
  frequency: 'monthly',
  day_of_month: new Date().getDate() > 28 ? 28 : new Date().getDate(),
  next_due_date: null,
  description: null,
  is_active: true,
})

const isEdit = computed(() => !!props.payment)

watch(
  () => props.payment,
  (val) => {
    if (val) {
      form.value = {
        name: val.name || '',
        amount: val.amount ? Number(val.amount) : null,
        type: val.type || 'expense',
        frequency: val.frequency || 'monthly',
        day_of_month: val.day_of_month || 1,
        next_due_date: val.next_due_date || null,
        description: val.description || null,
        is_active: val.is_active !== undefined ? val.is_active : true,
      }
    } else {
      form.value = {
        name: '',
        amount: null,
        type: 'expense',
        frequency: 'monthly',
        day_of_month: new Date().getDate() > 28 ? 28 : new Date().getDate(),
        next_due_date: null,
        description: null,
        is_active: true,
      }
    }
  },
  { immediate: true }
)

function handleSubmit() {
  submitted.value = true
  if (!form.value.name || !form.value.amount || !form.value.day_of_month || !form.value.next_due_date) return

  submitting.value = true
  try {
    const payload = {
      id: props.payment?.id || undefined,
      name: form.value.name,
      amount: form.value.amount,
      type: form.value.type,
      frequency: form.value.frequency,
      day_of_month: form.value.day_of_month,
      next_due_date: form.value.next_due_date,
      description: form.value.description || null,
      is_active: form.value.is_active,
    }
    emit('save', payload)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 300;
}
.modal-content {
  background: var(--color-neutral-0);
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 640px;
  margin: auto;
  padding: 12px 20px 20px;
  max-height: 90vh;
  overflow-y: auto;
}
[data-theme="dark"] .modal-content {
  background: var(--color-neutral-900);
}
.modal-handle {
  width: 40px;
  height: 4px;
  background: var(--color-neutral-300);
  border-radius: 2px;
  margin: 0 auto 12px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.modal-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin: 0;
}
.edit-form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-field { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.form-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-neutral-700);
}
.text-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  min-height: 44px;
}
.amount-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  min-height: 44px;
}
.amount-input.error { border-color: var(--color-error-400); }
.currency { font-size: var(--font-size-xl); color: var(--color-neutral-400); }
.amount-field {
  flex: 1;
  border: none;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  outline: none;
  background: transparent;
}
.form-select {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  color: var(--color-neutral-700);
  background: var(--color-neutral-0);
  min-height: 44px;
}
.type-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
}
.type-btn {
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-neutral-700);
  min-height: 44px;
  transition: var(--transition-fast);
}
.type-btn:hover { border-color: var(--color-primary-300); }
.type-btn.selected {
  border-color: var(--color-primary-500);
  background: var(--color-primary-50);
  color: var(--color-primary-700);
}
.form-check-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
}
.form-check-row input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}
.check-label {
  font-size: 0.9rem;
  color: var(--color-neutral-700);
}
.field-error {
  font-size: var(--font-size-xs);
  color: var(--color-error-500);
}
.submit-btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-neutral-0);
  background: var(--color-primary-600);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  transition: var(--transition-fast);
}
.submit-btn:hover:not(:disabled) { opacity: 0.9; }
.submit-btn:active:not(:disabled) { transform: scale(0.97); }
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
.fade-enter-active, .fade-leave-active { transition: opacity 200ms; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

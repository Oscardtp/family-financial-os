<template>
  <div class="card form-card">
    <h3 class="card-title">{{ title }}</h3>
    <form class="form" @submit.prevent="handleSubmit">
      <div v-if="fields.includes('name')" class="form-group">
        <label class="form-label">Nombre</label>
        <input v-model="form.name" class="form-input" type="text" required :placeholder="`Nombre del ${typeLabel}`">
      </div>
      <div v-if="fields.includes('type')" class="form-group">
        <label class="form-label">Tipo</label>
        <select v-model="form.type" class="form-select" required>
          <option value="" disabled>Seleccionar tipo</option>
          <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      <div v-if="fields.includes('value')" class="form-row">
        <div class="form-group">
          <label class="form-label">Valor</label>
          <input v-model.number="form.value" class="form-input" type="number" step="0.01" required min="0">
        </div>
        <div v-if="fields.includes('purchase_date')" class="form-group">
          <label class="form-label">Fecha de Compra</label>
          <input v-model="form.purchase_date" class="form-input" type="date">
        </div>
      </div>
      <div v-if="fields.includes('total_amount')" class="form-row">
        <div class="form-group">
          <label class="form-label">Monto Total</label>
          <input v-model.number="form.total_amount" class="form-input" type="number" step="0.01" required min="0">
        </div>
        <div class="form-group">
          <label class="form-label">Saldo Actual</label>
          <input v-model.number="form.current_balance" class="form-input" type="number" step="0.01" required min="0">
        </div>
      </div>
      <div v-if="fields.includes('interest_rate')" class="form-row">
        <div class="form-group">
          <label class="form-label">Tasa de Interés (%)</label>
          <input v-model.number="form.interest_rate" class="form-input" type="number" step="0.01" min="0">
        </div>
        <div class="form-group">
          <label class="form-label">Pago Mensual</label>
          <input v-model.number="form.monthly_payment" class="form-input" type="number" step="0.01" min="0">
        </div>
      </div>
      <div class="form-actions">
        <span v-if="formError" class="form-error">{{ formError }}</span>
        <button class="btn btn-primary" type="submit" :disabled="submitting">
          {{ submitting ? 'Creando...' : submitLabel }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  typeLabel: { type: String, default: 'elemento' },
  fields: { type: Array, required: true },
  typeOptions: { type: Array, default: () => [] },
  submitLabel: { type: String, default: 'Crear' },
})

const emit = defineEmits(['submit'])

const submitting = ref(false)
const formError = ref('')

const form = reactive(buildInitial())

function buildInitial() {
  const obj = {}
  for (const f of props.fields) {
    if (f === 'name' || f === 'type' || f === 'purchase_date') obj[f] = ''
    else obj[f] = 0
  }
  return obj
}

async function handleSubmit() {
  submitting.value = true
  formError.value = ''
  try {
    await emit('submit', { ...form })
    Object.assign(form, buildInitial())
  } catch (e) {
    formError.value = e?.message || 'No pudimos guardar. Intenta de nuevo.'
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
}
.form-select:focus { border-color: var(--color-primary-400); }
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

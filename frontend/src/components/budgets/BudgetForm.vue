<template>
  <div class="card">
    <h3 class="card-title">Crear nuevo presupuesto</h3>
    <form class="form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label class="form-label">Categoría</label>
        <select v-model.number="form.category_id" class="form-select" required>
          <option :value="0" disabled>Seleccionar categoría</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Monto mensual</label>
        <input v-model.number="form.amount" class="form-input" type="number" step="1000" min="0" required placeholder="500000">
      </div>
      <div class="form-actions">
        <span v-if="formError" class="form-error">{{ formError }}</span>
        <button class="btn btn-primary" type="submit" :disabled="submitting">
          {{ submitting ? 'Creando...' : 'Crear Presupuesto' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  initialMonth: { type: Number, required: true },
  initialYear: { type: Number, required: true },
})

const emit = defineEmits(['submit'])

const submitting = ref(false)
const formError = ref('')

const form = reactive({
  category_id: 0,
  amount: 0,
  month: props.initialMonth,
  year: props.initialYear,
})

async function handleSubmit() {
  submitting.value = true
  formError.value = ''
  try {
    await emit('submit', { ...form })
    form.category_id = 0
    form.amount = 0
  } catch (e) {
    formError.value = e?.message || 'No pudimos crear el presupuesto. Intenta de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--spacing-md); }
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-select {
  padding: var(--spacing-sm) var(--spacing-md); border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md); font-size: 0.875rem; outline: none;
}
.form-select:focus { border-color: var(--color-primary-400); }
.form-actions { display: flex; align-items: center; justify-content: flex-end; gap: var(--spacing-md); }
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
</style>

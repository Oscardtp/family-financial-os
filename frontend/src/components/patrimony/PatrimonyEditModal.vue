<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3 class="modal-title">{{ title }}</h3>
      <form class="form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">Nombre</label>
          <input v-model="form.name" class="form-input" type="text" required>
        </div>
        <div class="form-group">
          <label class="form-label">Tipo</label>
          <select v-model="form.type" class="form-select" required>
            <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">{{ valueLabel }}</label>
          <input v-model.number="form.value" class="form-input" type="number" step="0.01" required min="0">
        </div>
        <div class="form-actions">
          <span v-if="formError" class="form-error">{{ formError }}</span>
          <button class="btn btn-sm" type="button" @click="$emit('close')">Cancelar</button>
          <button class="btn btn-primary" type="submit" :disabled="submitting">
            {{ submitting ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Editar' },
  item: { type: Object, default: null },
  typeOptions: { type: Array, default: () => [] },
  valueLabel: { type: String, default: 'Valor' },
})

const emit = defineEmits(['close', 'saved'])

const form = reactive({ name: '', type: '', value: 0 })
const formError = ref('')
const submitting = ref(false)

watch(() => props.item, (item) => {
  if (item) {
    form.name = item.name || ''
    form.type = item.type || ''
    form.value = item.value ?? item.current_balance ?? 0
  }
}, { immediate: true })

async function handleSubmit() {
  submitting.value = true
  formError.value = ''
  try {
    emit('saved', { ...form })
  } catch (e) {
    formError.value = e?.message || 'Error al guardar'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: var(--color-neutral-0); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); width: 90%; max-width: 420px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.modal-title { font-size: 1rem; font-weight: 600; margin-bottom: var(--spacing-md); }
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md); font-size: 0.875rem; outline: none;
}
.form-select:focus { border-color: var(--color-primary-400); }
.form-actions {
  display: flex; align-items: center; justify-content: flex-end;
  gap: var(--spacing-md); margin-top: var(--spacing-sm);
}
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { background: var(--color-neutral-100); color: var(--color-neutral-700); }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
</style>

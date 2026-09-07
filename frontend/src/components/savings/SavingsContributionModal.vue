<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')" @keydown.escape="$emit('close')" role="dialog" aria-modal="true" :aria-label="`Contribuir a ${goal?.name}`">
    <div class="modal" @click.stop>
      <h3 class="modal-title">Contribuir a — {{ goal?.name }}</h3>
      <form class="form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">Monto</label>
          <div class="form-input-prefix">
            <span class="input-prefix">$</span>
            <input
              :value="fmtAmount.displayValue.value"
              @input="fmtAmount.onInput"
              class="form-input with-prefix"
              required
            >
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha</label>
          <input v-model="form.contribution_date" class="form-input" type="date" required>
        </div>
        <div class="form-actions">
          <span v-if="error" class="form-error">{{ error }}</span>
          <button class="btn btn-sm" type="button" @click="$emit('close')">Cancelar</button>
          <button class="btn btn-primary" type="submit" :disabled="submitting">
            {{ submitting ? 'Registrando...' : 'Registrar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'

const props = defineProps({
  show: { type: Boolean, default: false },
  goal: { type: Object, default: null },
})

const emit = defineEmits(['close', 'saved'])

const submitting = ref(false)
const error = ref('')
const fmtAmount = useFormattedNumber(0, { prefix: '$' })

const form = reactive({
  amount: 0,
  contribution_date: new Date().toISOString().split('T')[0],
})

watch(() => props.goal, () => {
  form.amount = 0
  form.contribution_date = new Date().toISOString().split('T')[0]
  error.value = ''
  fmtAmount.setInitial(0)
})

watch(() => fmtAmount.rawValue.value, (val) => { form.amount = val })

async function handleSubmit() {
  submitting.value = true
  error.value = ''
  try {
    const { default: api } = await import('@/services/api')
    await api.post(`/savings/goals/${props.goal.id}/contributions`, {
      amount: fmtAmount.rawValue.value,
      contribution_date: form.contribution_date,
    })
    emit('saved')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'No pudimos registrar la contribución. Revisa los datos e inténtalo de nuevo.'
  } finally {
    submitting.value = false
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

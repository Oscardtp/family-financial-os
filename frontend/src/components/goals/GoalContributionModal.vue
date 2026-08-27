<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')" @keydown.escape="$emit('close')" role="dialog" aria-modal="true" :aria-label="`Aportar a ${goal?.name}`">
    <div class="modal-content" @click.stop>
      <h3 class="modal-title">Aportar a "{{ goal?.name }}"</h3>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label" for="contribution-amount">¿Cuánto quieres aportar?</label>
          <div class="modal-amount-input" :class="{ error: amountError }">
            <span class="modal-currency">$</span>
            <input
              id="contribution-amount"
              ref="amountField"
              :value="amount"
              @input="$emit('update:amount', $event.target.value); validate($event.target.value)"
              type="number"
              class="modal-amount-field"
              placeholder="0"
              min="1"
            />
          </div>
          <span v-if="amountError" class="form-error">{{ amountError }}</span>
        </div>
        <div class="form-group">
          <label class="form-label" for="contribution-date">¿Cuándo?</label>
          <input
            id="contribution-date"
            :value="date"
            @input="$emit('update:date', $event.target.value)"
            type="date"
            class="form-input"
          />
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
        <button
          class="btn-confirm"
          @click="$emit('submit')"
          :disabled="!amount || submitting || !!amountError"
        >
          {{ submitting ? 'Guardando...' : 'Confirmar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  goal: { type: Object, default: null },
  amount: { type: String, default: '' },
  date: { type: String, default: '' },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit', 'update:amount', 'update:date'])

const amountError = ref('')
const amountField = ref(null)

function validate(val) {
  const num = parseFloat(val)
  if (isNaN(num) || num <= 0) {
    amountError.value = 'El monto debe ser mayor a $0'
  } else if (num > 100000000) {
    amountError.value = 'El monto es demasiado alto'
  } else {
    amountError.value = ''
  }
}

onMounted(() => {
  if (props.show) {
    setTimeout(() => amountField.value?.focus(), 100)
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: 24px;
  width: 90%;
  max-width: 400px;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--color-neutral-900);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-neutral-600);
}

.form-input {
  padding: 10px 12px;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  border-color: var(--color-primary-500);
}

.modal-amount-input {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  transition: border-color var(--transition-fast);
}

.modal-amount-input:focus-within {
  border-color: var(--color-primary-500);
}

.modal-amount-input.error {
  border-color: var(--color-error-500);
}

.modal-currency {
  font-size: 18px;
  color: var(--color-neutral-400);
}

.modal-amount-field {
  flex: 1;
  border: none;
  font-size: 18px;
  font-weight: 700;
  outline: none;
  background: transparent;
  font-family: var(--font-mono);
}

.form-error {
  font-size: 0.75rem;
  color: var(--color-error-600);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}

.btn-cancel {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
  padding: 8px 20px;
  border-radius: var(--radius-pill);
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  background: var(--color-neutral-200);
}

.btn-confirm {
  background: var(--color-primary-500);
  color: white;
  padding: 8px 20px;
  border-radius: var(--radius-pill);
  border: none;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.btn-confirm:hover {
  background: var(--color-primary-600);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.btn-confirm:disabled {
  background: var(--color-primary-300);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>

<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')" @keydown.escape="$emit('close')" role="dialog" aria-modal="true" aria-label="Editar meta">
    <div class="modal-content modal-wide" @click.stop>
      <h3 class="modal-title">Editar "{{ goal?.name }}"</h3>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label" for="edit-name">Nombre</label>
          <input id="edit-name" v-model="form.name" type="text" class="form-input" maxlength="100" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="edit-target">Monto objetivo</label>
            <div class="modal-amount-input">
              <span class="modal-currency">$</span>
              <input id="edit-target" v-model="form.target_amount" type="number" class="modal-amount-field" min="1" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label" for="edit-monthly">Aporte mensual</label>
            <div class="modal-amount-input">
              <span class="modal-currency">$</span>
              <input id="edit-monthly" v-model="form.monthly_contribution" type="number" class="modal-amount-field" min="0" />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="edit-date">Fecha objetivo</label>
            <input id="edit-date" v-model="form.target_date" type="date" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label" for="edit-priority">Prioridad</label>
            <select id="edit-priority" v-model="form.priority" class="form-input">
              <option value="low">Baja</option>
              <option value="medium">Media</option>
              <option value="high">Alta</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label" for="edit-type">Tipo de meta</label>
          <select id="edit-type" v-model="form.goal_type" class="form-input">
            <option value="savings">Ahorro</option>
            <option value="investment">Inversión</option>
          </select>
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
        <button class="btn-confirm" @click="handleSubmit" :disabled="submitting">
          {{ submitting ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  goal: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])

const form = reactive({
  name: '',
  target_amount: '',
  monthly_contribution: '',
  target_date: '',
  priority: 'medium',
  goal_type: 'savings',
})

watch(
  () => props.goal,
  (g) => {
    if (g) {
      form.name = g.name
      form.target_amount = g.target_amount
      form.monthly_contribution = g.monthly_contribution || ''
      form.target_date = g.target_date || ''
      form.priority = g.priority || 'medium'
      form.goal_type = g.goal_type || 'savings'
    }
  },
  { immediate: true }
)

function handleSubmit() {
  if (!props.goal) return
  emit('submit', { ...form })
}
</script>

<style scoped>
.modal-content {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: 24px;
  width: 90%;
  max-width: 520px;
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



.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
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

@media (max-width: 640px) {
  .modal-content {
    padding: 16px;
    margin: 16px;
  }
}
</style>

<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')" @keydown.escape="$emit('close')" role="dialog" aria-modal="true" aria-label="Crear nueva meta">
    <div class="modal-content modal-wide" @click.stop>
      <h3 class="modal-title">Nueva meta</h3>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label" for="goal-name">¿Qué estás juntando?</label>
          <input id="goal-name" v-model="form.name" type="text" class="form-input" placeholder="Ej: Viaje, Fondo de emergencia, Nuevo carro" maxlength="100" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="goal-target">¿Cuánto necesitas?</label>
            <div class="modal-amount-input">
              <span class="modal-currency">$</span>
              <input id="goal-target" v-model="form.target_amount" type="number" class="modal-amount-field" placeholder="0" min="1" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label" for="goal-monthly">¿Cuánto puedes ahorrar al mes?</label>
            <div class="modal-amount-input">
              <span class="modal-currency">$</span>
              <input id="goal-monthly" v-model="form.monthly_contribution" type="number" class="modal-amount-field" placeholder="0" min="0" />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label" for="goal-date">¿Para cuándo?</label>
            <input id="goal-date" v-model="form.target_date" type="date" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label" for="goal-type">Tipo</label>
            <select id="goal-type" v-model="form.goal_type" class="form-input">
              <option value="savings">Ahorro</option>
              <option value="investment">Inversión</option>
            </select>
          </div>
        </div>
        <div v-if="form.goal_type === 'investment'" class="form-row">
          <div class="form-group">
            <label class="form-label" for="goal-return">Rendimiento esperado (% EA)</label>
            <input id="goal-return" v-model="form.expected_return_rate" type="number" class="form-input" placeholder="Ej: 9" min="0" step="0.1" />
          </div>
          <div class="form-group">
            <label class="form-label" for="goal-horizon">Horizonte (meses)</label>
            <input id="goal-horizon" v-model="form.horizon_months" type="number" class="form-input" placeholder="Ej: 24" min="1" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label" for="goal-priority">Prioridad</label>
          <select id="goal-priority" v-model="form.priority" class="form-input">
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
          </select>
        </div>
        <p v-if="smartSummary" class="smart-summary">{{ smartSummary }}</p>
      </div>
      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
        <button
          class="btn-confirm"
          @click="handleSubmit"
          :disabled="!form.name || !form.target_amount || submitting"
        >
          {{ submitting ? 'Creando...' : 'Crear meta' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useSmartCalculator } from '@/composables/useSmartCalculator'

const props = defineProps({
  show: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])

const { calcSmartFields } = useSmartCalculator()

const form = reactive({
  name: '',
  target_amount: '',
  monthly_contribution: '',
  target_date: '',
  goal_type: 'savings',
  expected_return_rate: '',
  horizon_months: '',
  priority: 'medium',
})

const smartSummary = computed(() => {
  const target = parseFloat(form.target_amount) || 0
  const monthly = parseFloat(form.monthly_contribution) || 0
  if (target <= 0) return ''
  const result = calcSmartFields(target, form.target_date, monthly, 0)
  return result.summary || ''
})

watch(
  () => form.target_date,
  () => {
    if (form.target_date && !form.monthly_contribution && form.target_amount) {
      const target = parseFloat(form.target_amount)
      if (target > 0) {
        const now = new Date()
        const targetDate = new Date(form.target_date + 'T00:00:00')
        const months = Math.max((targetDate.getFullYear() - now.getFullYear()) * 12 + (targetDate.getMonth() - now.getMonth()), 1)
        form.monthly_contribution = Math.ceil(target / months)
      }
    }
  }
)

function handleSubmit() {
  if (!form.name || !form.target_amount) return
  emit('submit', { ...form })
}
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

.smart-summary {
  font-size: 0.8125rem;
  color: var(--color-primary-600);
  background: var(--color-primary-50);
  padding: 10px 12px;
  border-radius: var(--radius-md);
  margin: 0;
  line-height: 1.5;
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

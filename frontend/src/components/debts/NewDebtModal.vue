<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="$emit('close')">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Crear Deuda</h3>
            <button class="modal-close" @click="$emit('close')">&times;</button>
          </div>

          <form class="debt-form" @submit.prevent="submitCreate">
            <div class="form-group">
              <label class="form-label">Nombre de la deuda</label>
              <input
                v-model="createForm.name"
                type="text"
                class="form-input"
                placeholder="Ej: Tarjeta de crédito Daviplata"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Acreedor</label>
              <input
                v-model="createForm.creditor"
                type="text"
                class="form-input"
                placeholder="Ej: Daviplata"
                required
              />
            </div>

            <div class="form-row">
              <div class="form-group">
              <label class="form-label">Monto Original</label>
              <div class="input-prefix">
                <input
                  :value="fmtAmount.displayValue.value"
                  @input="fmtAmount.onInput"
                  @focus="fmtAmount.onFocus"
                  class="form-input with-prefix"
                  required
                />
              </div>
              </div>

              <div class="form-group">
              <label class="form-label">Saldo Actual</label>
              <div class="input-prefix">
                <input
                  :value="fmtBalance.displayValue.value"
                  @input="fmtBalance.onInput"
                  @focus="fmtBalance.onFocus"
                  class="form-input with-prefix"
                  required
                />
              </div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Tasa Interes (%)</label>
                <input
                  v-model.number="createForm.interest_rate"
                  type="number"
                  step="0.1"
                  min="0"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Tipo de Tasa</label>
                <select v-model="createForm.interest_rate_type" class="form-input">
                  <option value="EA">EA (Efectiva Anual)</option>
                  <option value="EM">EM (Efectiva Mensual)</option>
                  <option value="nominal">Nominal Anual</option>
                  <option value="daily">Diaria</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
              <label class="form-label">Pago Minimo</label>
              <div class="input-prefix">
                <input
                  :value="fmtMinPay.displayValue.value"
                  @input="fmtMinPay.onInput"
                  @focus="fmtMinPay.onFocus"
                  class="form-input with-prefix"
                  required
                />
              </div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Tipo de Deuda</label>
                <select v-model="createForm.debt_type" class="form-input">
                  <option value="loan">Prestamo</option>
                  <option value="credit_card">Tarjeta de crédito</option>
                  <option value="mortgage">Hipoteca</option>
                  <option value="personal">Personal</option>
                  <option value="other">Otro</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Dia Vencimiento</label>
                <input
                  v-model.number="createForm.due_day"
                  type="number"
                  min="1"
                  max="31"
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Fecha Inicio</label>
              <input
                v-model="createForm.start_date"
                type="date"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Nota (opcional)</label>
              <input
                v-model="createForm.note"
                type="text"
                class="form-input"
                placeholder="Ej: Pago fijo mensual"
              />
            </div>

            <p v-if="createError" class="form-error">{{ createError }}</p>

            <button type="submit" class="submit-btn" :disabled="creating">
              {{ creating ? 'Creando...' : 'Crear Deuda' }}
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import api from '@/services/api'

const props = defineProps({
  show: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'created'])

const createForm = reactive({
  name: '',
  creditor: '',
  interest_rate: 0,
  interest_rate_type: 'EA',
  debt_type: 'loan',
  due_day: 1,
  start_date: new Date().toISOString().split('T')[0],
  note: ''
})

const createError = ref('')
const creating = ref(false)

const fmtAmount = useFormattedNumber(0, { prefix: '$' })
const fmtBalance = useFormattedNumber(0, { prefix: '$' })
const fmtMinPay = useFormattedNumber(0, { prefix: '$' })

watch(() => props.show, (val) => {
  if (val) {
    createForm.name = ''
    createForm.creditor = ''
    createForm.interest_rate = 0
    createForm.interest_rate_type = 'EA'
    createForm.debt_type = 'loan'
    createForm.due_day = 1
    createForm.start_date = new Date().toISOString().split('T')[0]
    createForm.note = ''
    fmtAmount.setInitial(0)
    fmtBalance.setInitial(0)
    fmtMinPay.setInitial(0)
    createError.value = ''
  }
})

async function submitCreate() {
  creating.value = true
  createError.value = ''

  try {
    await api.post('/debts', {
      name: createForm.name,
      creditor: createForm.creditor,
      total_amount: fmtAmount.rawValue.value,
      current_balance: fmtBalance.rawValue.value || fmtAmount.rawValue.value,
      interest_rate: createForm.interest_rate,
      interest_rate_type: createForm.interest_rate_type,
      minimum_payment: fmtMinPay.rawValue.value,
      debt_type: createForm.debt_type,
      due_day: createForm.due_day,
      start_date: createForm.start_date || new Date().toISOString().split('T')[0],
      note: createForm.note || null
    })
    emit('created')
    emit('close')
  } catch (e) {
    createError.value = e.response?.data?.detail || 'No pudimos crear la deuda. Intenta de nuevo.'
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--spacing-md);
}

.modal-content {
  background: var(--color-neutral-0);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--color-neutral-900);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-neutral-500);
  line-height: 1;
}

.debt-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}



select.form-input {
  cursor: pointer;
}

.input-prefix {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.input-prefix:focus-within {
  border-color: var(--color-primary-500);
}

.prefix {
  padding: var(--spacing-md);
  background: var(--color-neutral-100);
  color: var(--color-neutral-500);
  font-size: 14px;
  font-weight: 500;
  border-right: 1px solid var(--color-neutral-200);
}

.form-input.with-prefix {
  border: none;
  border-radius: 0;
  flex: 1;
}

.form-input.with-prefix:focus {
  border: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.form-error {
  color: var(--color-error-600);
  font-size: 13px;
  margin: 0;
}

.submit-btn {
  padding: var(--spacing-md);
  background: var(--color-primary-500);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-600);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

[data-theme="dark"] .modal-content {
  background: var(--color-neutral-100);
}
</style>
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="$emit('close')">
        <FocusTrap :visible="show">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>Crear Deuda</h3>
              <button class="modal-close" @click="$emit('close')">&times;</button>
            </div>

          <form class="debt-form" @submit.prevent="submitCreate" aria-live="polite">
            <div class="form-group">
              <label class="form-label" for="debt-name">Nombre de la deuda</label>
              <input
                v-model="createForm.name"
                type="text"
                class="form-input"
                placeholder="Ej: Tarjeta de crédito Daviplata"
                id="debt-name"
                name="name"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="debt-creditor">Acreedor</label>
              <input
                v-model="createForm.creditor"
                type="text"
                class="form-input"
                placeholder="Ej: Daviplata"
                id="debt-creditor"
                name="creditor"
                required
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="debt-amount">Monto Original</label>
                <div class="input-prefix">
                  <input
                    :value="fmtAmount.displayValue.value"
                    @input="fmtAmount.onInput"
                    @focus="fmtAmount.onFocus"
                    class="form-input with-prefix"
                    id="debt-amount"
                    name="amount"
                    required
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="debt-balance">Saldo Actual</label>
                <div class="input-prefix">
                  <input
                    :value="fmtBalance.displayValue.value"
                    @input="fmtBalance.onInput"
                    @focus="fmtBalance.onFocus"
                    class="form-input with-prefix"
                    id="debt-balance"
                    name="current_balance"
                    required
                  />
                </div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="debt-interest-rate">Tasa Interes (%)</label>
                <input
                  v-model.number="createForm.interest_rate"
                  type="number"
                  step="0.1"
                  min="0"
                  class="form-input"
                  id="debt-interest-rate"
                  name="interest_rate"
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="debt-rate-type">Tipo de Tasa</label>
                <select v-model="createForm.interest_rate_type" class="form-input" id="debt-rate-type" name="interest_rate_type">
                  <option value="EA">EA (Efectiva Anual)</option>
                  <option value="EM">EM (Efectiva Mensual)</option>
                  <option value="nominal">Nominal Anual</option>
                  <option value="daily">Diaria</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="debt-min-payment">Pago Minimo</label>
                <div class="input-prefix">
                  <input
                    :value="fmtMinPay.displayValue.value"
                    @input="fmtMinPay.onInput"
                    @focus="fmtMinPay.onFocus"
                    class="form-input with-prefix"
                    id="debt-min-payment"
                    name="minimum_payment"
                    required
                  />
                </div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="debt-type">Tipo de Deuda</label>
                <select v-model="createForm.debt_type" class="form-input" id="debt-type" name="debt_type">
                  <option value="loan">Prestamo</option>
                  <option value="credit_card">Tarjeta de crédito</option>
                  <option value="mortgage">Hipoteca</option>
                  <option value="personal">Personal</option>
                  <option value="other">Otro</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label" for="debt-due-day">Dia Vencimiento</label>
                <input
                  v-model.number="createForm.due_day"
                  type="number"
                  min="1"
                  max="31"
                  class="form-input"
                  id="debt-due-day"
                  name="due_day"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="debt-start-date">Fecha Inicio</label>
              <input
                v-model="createForm.start_date"
                type="date"
                class="form-input"
                id="debt-start-date"
                name="start_date"
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="debt-note">Nota (opcional)</label>
              <input
                v-model="createForm.note"
                type="text"
                class="form-input"
                placeholder="Ej: Pago fijo mensual"
                id="debt-note"
                name="note"
              />
            </div>

            <p v-if="createError" class="form-error" role="alert" aria-live="assertive">{{ createError }}</p>

            <button type="submit" class="submit-btn" :disabled="creating">
              {{ creating ? 'Creando...' : 'Crear Deuda' }}
            </button>
          </form>
        </div>
        </FocusTrap>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import api from '@/services/api'
import FocusTrap from '@/components/FocusTrap.vue'
import { getLocalDateString } from '@/composables/useDateFormat'

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
  start_date: getLocalDateString(),
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
    createForm.start_date = getLocalDateString()
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
      start_date: createForm.start_date || getLocalDateString(),
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
  transition: transform var(--transition-fast);
}
.modal-close:active { transform: scale(0.94); }

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

.prefix {
  padding: var(--spacing-md);
  background: var(--color-neutral-100);
  color: var(--color-neutral-500);
  font-size: 14px;
  font-weight: 500;
  border-right: 1px solid var(--color-neutral-200);
  min-height: 44px;
}

.form-input.with-prefix {
  border: none;
  border-radius: 0;
  flex: 1;
  min-height: 44px;
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
  transition: transform var(--transition-fast), background var(--transition-fast);
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-600);
}
.submit-btn:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }

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
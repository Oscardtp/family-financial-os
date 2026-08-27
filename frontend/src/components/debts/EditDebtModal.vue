<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="$emit('close')">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Editar Deuda</h3>
            <button class="modal-close" @click="$emit('close')">&times;</button>
          </div>

          <form class="debt-form" @submit.prevent="submitEdit">
            <div class="form-group">
              <label class="form-label">Nombre</label>
              <input
                v-model="editForm.name"
                type="text"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Acreedor</label>
              <input
                v-model="editForm.creditor"
                type="text"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Saldo Actual</label>
              <div class="input-prefix">
                <span class="prefix">$</span>
                <input
                  :value="fmtBalance.displayValue.value"
                  @input="fmtBalance.onInput"
                  @focus="fmtBalance.onFocus"
                  class="form-input with-prefix"
                  required
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Tasa Interes (%)</label>
                <input
                  v-model.number="editForm.interest_rate"
                  type="number"
                  step="0.1"
                  min="0"
                  class="form-input"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">Pago Minimo</label>
                <div class="input-prefix">
                  <span class="prefix">$</span>
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

            <div class="form-group">
              <label class="form-label">Dia Vencimiento</label>
              <input
                v-model.number="editForm.due_day"
                type="number"
                min="1"
                max="31"
                class="form-input"
                required
              />
            </div>

            <p v-if="editError" class="form-error">{{ editError }}</p>

            <button type="submit" class="submit-btn" :disabled="editing">
              {{ editing ? 'Guardando...' : 'Guardar Cambios' }}
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
  show: { type: Boolean, default: false },
  debt: { type: Object, default: null }
})

const emit = defineEmits(['close', 'updated'])

const editForm = reactive({
  name: '',
  creditor: '',
  interest_rate: 0,
  due_day: 15
})

const editError = ref('')
const editing = ref(false)

const fmtBalance = useFormattedNumber(0, { prefix: '$' })
const fmtMinPay = useFormattedNumber(0, { prefix: '$' })

watch(() => props.show, (val) => {
  if (val && props.debt) {
    editForm.name = props.debt.name || ''
    editForm.creditor = props.debt.creditor || ''
    editForm.interest_rate = props.debt.interest_rate || 0
    editForm.due_day = props.debt.due_day || 15
    fmtBalance.setInitial(props.debt.current_balance || 0)
    fmtMinPay.setInitial(props.debt.minimum_payment || 0)
    editError.value = ''
  }
})

async function submitEdit() {
  if (!props.debt?.id) return

  editing.value = true
  editError.value = ''

  try {
    await api.put(`/debts/${props.debt.id}`, {
      name: editForm.name,
      creditor: editForm.creditor,
      current_balance: fmtBalance.rawValue.value,
      interest_rate: editForm.interest_rate,
      minimum_payment: fmtMinPay.rawValue.value,
      due_day: editForm.due_day
    })
    emit('updated')
    emit('close')
  } catch (e) {
    editError.value = e.response?.data?.detail || 'No pudimos guardar los cambios. Intenta de nuevo.'
  } finally {
    editing.value = false
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

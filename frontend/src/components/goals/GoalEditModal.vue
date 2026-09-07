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
              <input
                id="edit-target"
                :value="displayTarget"
                @input="onTargetInput"
                @focus="onTargetFocus"
                class="modal-amount-field"
                min="1"
              />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label" for="edit-monthly">Aporte mensual</label>
            <div class="modal-amount-input">
              <span class="modal-currency">$</span>
              <input
                id="edit-monthly"
                :value="displayMonthly"
                @input="onMonthlyInput"
                @focus="onMonthlyFocus"
                class="modal-amount-field"
                min="0"
              />
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
import { reactive, watch, computed } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'

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

let fmtTarget = useFormattedNumber(0, { prefix: '' })
const displayTarget = computed(() => fmtTarget.displayValue.value)
const onTargetInput = (event) => fmtTarget.onInput(event)
const onTargetFocus = (event) => fmtTarget.onFocus(event)

let fmtMonthly = useFormattedNumber(0, { prefix: '' })
const displayMonthly = computed(() => fmtMonthly.displayValue.value)
const onMonthlyInput = (event) => fmtMonthly.onInput(event)
const onMonthlyFocus = (event) => fmtMonthly.onFocus(event)

watch(
  () => props.goal,
  (g) => {
    if (g) {
      form.name = g.name
      form.target_date = g.target_date || ''
      form.priority = g.priority || 'medium'
      form.goal_type = g.goal_type || 'savings'
      fmtTarget.setInitial(g.target_amount || 0)
      fmtMonthly.setInitial(g.monthly_contribution || 0)
    }
  },
  { immediate: true }
)

function handleSubmit() {
  if (!props.goal) return
  emit('submit', {
    ...form,
    target_amount: fmtTarget.rawValue.value,
    monthly_contribution: fmtMonthly.rawValue.value || null,
  })
}
</script>

<style scoped>
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

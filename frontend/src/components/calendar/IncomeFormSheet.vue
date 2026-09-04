<template>
  <div class="sheet-backdrop" @click.self="$emit('close')">
    <div class="sheet">
      <div class="drag-handle"></div>
      <button class="sheet-close" @click="$emit('close')" aria-label="Cerrar">
        <X :size="18" />
      </button>
      <h3 class="sheet-title">Registrar ingreso</h3>

      <div class="amount-display amount-display--income">
        <span class="amount-prefix">$</span>
        <input
          v-model="form.amount"
          type="number"
          min="1"
          required
          placeholder="0"
          class="amount-input-clean"
          autofocus
        />
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="field-group">
          <label class="field-label">
            Fecha
            <input v-model="form.due_date" type="date" required class="tyba-input" />
          </label>
        </div>

        <div class="field-group">
          <label class="field-label">
            ¿De dónde?
            <input
              v-model="form.title"
              type="text"
              placeholder="Ej: Quincena, Freelance..."
              class="tyba-input"
            />
          </label>
        </div>

        <div class="field-group">
          <label class="field-label">
            Notas
            <textarea
              v-model="form.notes"
              rows="2"
              placeholder="Opcional..."
              class="tyba-textarea"
            ></textarea>
          </label>
        </div>

        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="form-actions">
          <button type="button" class="btn-ghost" @click="$emit('close')">Cancelar</button>
          <button type="submit" class="btn-primary btn-primary--income" :disabled="submitting">
            {{ submitting ? 'Guardando...' : 'Registrar ingreso' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { X } from 'lucide-vue-next'
import api from '@/services/api'
import './sheet-styles.css'

const props = defineProps({
  date: { type: String, required: true },
})

const emit = defineEmits(['close', 'created'])

const form = ref({
  amount: '',
  due_date: props.date,
  title: '',
  notes: '',
})

const error = ref(null)
const submitting = ref(false)

async function handleSubmit() {
  error.value = null
  if (!form.value.amount || !form.value.due_date) {
    error.value = 'Completa el monto y la fecha.'
    return
  }
  submitting.value = true
  try {
    await api.post('/events', {
      title: form.value.title || 'Ingreso',
      type: 'income',
      amount: parseFloat(form.value.amount),
      due_date: form.value.due_date,
      notes: form.value.notes || null,
      visibility: 'confirmed',
    })
    emit('created')
  } catch (e) {
    error.value = 'No pudimos guardar el ingreso. Intenta de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>

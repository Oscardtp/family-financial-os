<template>
  <div class="sheet-backdrop" @click.self="$emit('close')">
    <div class="sheet">
      <div class="drag-handle"></div>
      <button class="sheet-close" @click="$emit('close')" aria-label="Cerrar">
        <X :size="18" />
      </button>
      <h3 class="sheet-title">Editar evento</h3>

      <div class="amount-display" :class="{ 'amount-display--income': original.type === 'income' }">
        <span class="amount-prefix">$</span>
        <input
          v-model.number="form.amount"
          type="number"
          min="1"
          required
          placeholder="0"
          class="amount-input-clean"
        />
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="field-group">
          <label class="field-label">
            Título
            <input
              v-model="form.title"
              type="text"
              required
              placeholder="¿Qué es este pago?"
              class="tyba-input"
            />
          </label>
        </div>

        <div class="field-group">
          <label class="field-label">
            Fecha
            <input v-model="form.due_date" type="date" required class="tyba-input" />
          </label>
        </div>

        <div v-if="original.type === 'expense' && form.category_id" class="field-group">
          <label class="field-label">
            Categoría
            <select v-model="form.category_id" class="tyba-select">
              <option :value="null" disabled>Seleccionar</option>
              <option v-for="cat in expenseCategories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
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
          <button type="submit" class="btn-primary" :disabled="submitting">
            {{ submitting ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { X } from 'lucide-vue-next'
import api from '@/services/api'
import './sheet-styles.css'

const props = defineProps({
  event: { type: Object, required: true },
})

const emit = defineEmits(['close', 'updated'])

const original = computed(() => props.event)

const form = ref({
  title: props.event.title || '',
  amount: props.event.amount || 0,
  due_date: props.event.due_date || '',
  category_id: props.event.category_id || null,
  notes: props.event.notes || '',
})

const error = ref(null)
const submitting = ref(false)
const categories = ref([])

const expenseCategories = computed(() =>
  categories.value.filter(c => c.type === 'expense')
)

onMounted(async () => {
  try {
    const res = await api.get('/categories')
    categories.value = res.data
  } catch {
    categories.value = []
  }
})

async function handleSubmit() {
  error.value = null
  if (!form.value.title || !form.value.amount || !form.value.due_date) {
    error.value = 'Completa todos los campos obligatorios.'
    return
  }
  submitting.value = true
  try {
    await api.put(`/events/${original.value.id}`, {
      title: form.value.title,
      amount: parseFloat(form.value.amount),
      due_date: form.value.due_date,
      category_id: form.value.category_id,
      notes: form.value.notes || null,
    })
    emit('updated')
  } catch (e) {
    error.value = 'No pudimos guardar los cambios. Intenta de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>

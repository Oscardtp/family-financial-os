<template>
  <div class="categories-page">
    <div class="page-header">
      <h2 class="page-title">
        Categorías
      </h2>
    </div>

    <div
      v-if="loading"
      class="loading-state"
    >
      <div class="spinner" />
      <span>Cargando categorías...</span>
    </div>

    <div
      v-else-if="error"
      class="error-state"
    >
      <span>{{ error }}</span>
      <button
        class="btn btn-sm"
        @click="loadCategories"
      >
        Reintentar
      </button>
    </div>

    <template v-else>
      <div class="categories-grid">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="category-card"
        >
          <div
            class="category-icon"
            :style="{ background: cat.color || '#e5e7eb' }"
          >
            {{ cat.icon || cat.name.charAt(0) }}
          </div>
          <div class="category-info">
            <span class="category-name">{{ cat.name }}</span>
            <span
              class="category-type-badge"
              :class="'type-' + cat.type"
            >
              {{ cat.type === 'income' ? 'Ingreso' : 'Gasto' }}
            </span>
          </div>
          <button
            class="btn btn-sm btn-danger"
            @click="deleteCategory(cat.id)"
          >
            X
          </button>
        </div>

        <div
          v-if="!categories.length"
          class="empty-state"
        >
          <p>No tienes categorías creadas</p>
        </div>
      </div>

      <div class="card form-card">
        <h3 class="card-title">
          Nueva Categoria
        </h3>
        <form
          class="form"
          @submit.prevent="createCategory"
        >
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nombre</label>
              <input
                v-model="form.name"
                class="form-input"
                type="text"
                required
                placeholder="Nombre de la categoría"
              >
            </div>
            <div class="form-group">
              <label class="form-label">Tipo</label>
              <select
                v-model="form.type"
                class="form-select"
                required
              >
                <option value="income">
                  Ingreso
                </option>
                <option value="expense">
                  Gasto
                </option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Icono (opcional)</label>
              <input
                v-model="form.icon"
                class="form-input"
                type="text"
                placeholder="Emoji o texto"
              >
            </div>
            <div class="form-group">
              <label class="form-label">Color (opcional)</label>
              <input
                v-model="form.color"
                class="form-input"
                type="color"
              >
            </div>
          </div>
          <div class="form-actions">
            <span
              v-if="formError"
              class="form-error"
            >{{ formError }}</span>
            <button
              class="btn btn-primary"
              type="submit"
              :disabled="submitting"
            >
              {{ submitting ? 'Creando...' : 'Crear Categoría' }}
            </button>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/services/api'

const categories = ref([])
const loading = ref(true)
const error = ref('')
const submitting = ref(false)
const formError = ref('')

const form = reactive({
  name: '',
  type: 'expense',
  icon: '',
  color: '#6366f1',
})

async function loadCategories() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/categories')
    categories.value = data
  } catch (e) {
    error.value = 'No pudimos cargar tus categorías. Intenta de nuevo.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function createCategory() {
  submitting.value = true
  formError.value = ''
  try {
    const payload = { name: form.name, type: form.type }
    if (form.icon) payload.icon = form.icon
    if (form.color) payload.color = form.color
    const { data } = await api.post('/categories', payload)
    categories.value.push(data)
    form.name = ''
    form.type = 'expense'
    form.icon = ''
    form.color = '#6366f1'
  } catch (e) {
    formError.value = e.response?.data?.detail || 'No pudimos crear la categoría. Intenta de nuevo.'
  } finally {
    submitting.value = false
  }
}

async function deleteCategory(id) {
  if (!confirm('Eliminar esta categoría?')) return
  try {
    await api.delete(`/categories/${id}`)
    categories.value = categories.value.filter((c) => c.id !== id)
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.categories-page { max-width: 960px; margin: 0 auto; }
.page-header { margin-bottom: var(--spacing-xl); }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}
.category-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}
.category-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
  color: white;
}
.category-info { flex: 1; }
.category-name { display: block; font-weight: 600; font-size: 0.9rem; color: var(--color-neutral-900); }
.category-type-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  margin-top: 4px;
}
.type-income { background: var(--color-success-100); color: var(--color-success-700); }
.type-expense { background: var(--color-error-100); color: var(--color-error-700); }
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-neutral-400);
  font-size: 0.875rem;
}
.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: var(--spacing-md);
}
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.form-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  outline: none;
}
.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
.btn-danger {
  background: var(--color-error-600);
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
}
.btn-danger:hover { background: var(--color-error-700); }

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .categories-page {
    padding: 0;
  }
  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>

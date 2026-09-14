<template>
  <div class="categories-tab">
    <div v-if="catLoading" class="loading-state">
      <SkeletonLoader v-for="n in 4" :key="n" variant="card" />
    </div>

    <template v-else>
      <div class="categories-grid">
        <div v-for="cat in categories" :key="cat.id" class="category-card" :class="'category-' + cat.type">
          <div class="category-icon" :style="{ background: cat.color || 'var(--color-neutral-200)' }">
            <span class="category-icon-text">{{ cat.icon || cat.name.charAt(0).toUpperCase() }}</span>
          </div>
          <div class="category-info">
            <span class="category-name">{{ cat.name }}</span>
            <span class="category-type-badge" :class="'type-' + cat.type">
              {{ cat.type === 'income' ? 'Ingreso' : 'Gasto' }}
            </span>
          </div>
          <button class="btn-icon-danger" @click="confirmDeleteCategory(cat.id)" aria-label="Eliminar categoría">
            <X :size="14" />
          </button>
        </div>

        <div v-if="!categories.length" class="empty-state">
          <Tag :size="32" class="empty-icon" />
          <p>No tienes categorías creadas</p>
          <span class="empty-hint">Crea tu primera categoría para organizar tus movimientos</span>
        </div>
      </div>

      <div class="card form-card">
        <h3 class="section-title">Nueva categoría</h3>
        <form class="form" @submit.prevent="createCategory">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="category-name">Nombre</label>
              <input v-model="catForm.name" class="form-input" type="text" required placeholder="Nombre de la categoría" id="category-name" name="name" autocomplete="off" />
            </div>
            <div class="form-group">
              <label class="form-label" for="category-type">Tipo</label>
              <select v-model="catForm.type" class="form-select" required id="category-type" name="type">
                <option value="income">Ingreso</option>
                <option value="expense">Gasto</option>
              </select>
            </div>
          </div>
          <div class="form-row form-row-tertiary">
            <div class="form-group">
              <label class="form-label" for="category-icon">Icono (opcional)</label>
              <input v-model="catForm.icon" class="form-input" type="text" placeholder="Emoji o texto" id="category-icon" name="icon" autocomplete="off" />
            </div>
            <div class="form-group">
              <label class="form-label" for="category-color">Color</label>
              <div class="color-input-wrap">
                <input v-model="catForm.color" class="form-input color-input" type="color" id="category-color" name="color" />
                <span class="color-preview" :style="{ background: catForm.color }"></span>
              </div>
            </div>
          </div>
          <div class="form-actions">
            <span v-if="catFormError" class="form-error" role="alert" aria-live="assertive">{{ catFormError }}</span>
            <button class="btn btn-primary" type="submit" :disabled="catSubmitting">
              {{ catSubmitting ? 'Creando...' : 'Crear categoría' }}
            </button>
          </div>
        </form>
      </div>
    </template>

    <ConfirmDialog
      v-model="showCatConfirm"
      title="Eliminar categoría"
      message="¿Seguro que quieres eliminar esta categoría? Se perderán todos los datos asociados."
      confirm-text="Eliminar"
      cancel-text="Cancelar"
      type="danger"
      @confirm="handleDeleteCategoryConfirm"
      @cancel="showCatConfirm = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Tag, X } from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const toast = useToast()

const categories = ref([])
const catLoading = ref(true)
const catSubmitting = ref(false)
const catFormError = ref('')
const catForm = reactive({ name: '', type: 'expense', icon: '', color: 'var(--color-secondary-500)' })

const catToDelete = ref(null)
const showCatConfirm = ref(false)

function confirmDeleteCategory(id) {
  catToDelete.value = id
  showCatConfirm.value = true
}

async function handleDeleteCategoryConfirm() {
  if (!catToDelete.value) return
  try {
    await api.delete(`/categories/${catToDelete.value}`)
    categories.value = categories.value.filter(c => c.id !== catToDelete.value)
    toast.success('Categoría eliminada')
  } catch {
    toast.error('No pudimos eliminar la categoría')
  } finally {
    showCatConfirm.value = false
    catToDelete.value = null
  }
}

async function loadCategories() {
  catLoading.value = true
  try {
    const { data } = await api.get('/categories')
    categories.value = data
  } catch {
    toast.error('No pudimos cargar las categorías')
  } finally {
    catLoading.value = false
  }
}

async function createCategory() {
  catSubmitting.value = true
  catFormError.value = ''
  try {
    const payload = { name: catForm.name, type: catForm.type }
    if (catForm.icon) payload.icon = catForm.icon
    if (catForm.color) payload.color = catForm.color
    const { data } = await api.post('/categories', payload)
    categories.value.push(data)
    catForm.name = ''
    catForm.type = 'expense'
    catForm.icon = ''
    catForm.color = 'var(--color-secondary-500)'
    toast.success('Categoría creada')
  } catch (e) {
    catFormError.value = e.response?.data?.detail || 'No pudimos crear la categoría'
  } finally {
    catSubmitting.value = false
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.category-card {
  position: relative;
  overflow: hidden;
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  border: 1px solid var(--color-neutral-100);
}
.category-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}
.category-income::before { background: var(--color-success-500); }
.category-expense::before { background: var(--color-error-500); }
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
.category-icon-text { font-weight: 600; font-size: 1rem; }
.category-info { flex: 1; min-width: 0; }
.category-name { display: block; font-weight: 600; font-size: 0.85rem; color: var(--color-neutral-900); }
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

.form-card { margin-bottom: var(--spacing-md); }
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.form-row-tertiary { margin-top: var(--spacing-xs); }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.form-label { font-size: 0.8rem; font-weight: 500; color: var(--color-neutral-700); }
.form-input, .form-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  outline: none;
  transition: border-color var(--transition-fast);
}
.color-input-wrap { display: flex; align-items: center; gap: var(--spacing-sm); }
.color-input { width: 48px; height: 40px; padding: 2px; cursor: pointer; }
.color-preview {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-neutral-200);
  flex-shrink: 0;
}
.form-actions { display: flex; align-items: center; justify-content: flex-end; gap: var(--spacing-md); margin-top: var(--spacing-sm); }
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn-icon-danger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: none;
  border: none;
  color: var(--color-neutral-400);
  cursor: pointer;
  padding: 0;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.btn-icon-danger:hover { color: var(--color-error-500); background: var(--color-error-50); }
.btn-icon-danger:active:not(:disabled) { transform: scale(0.94); }

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
  .categories-grid { grid-template-columns: 1fr; }
}
</style>

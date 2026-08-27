<template>
  <div class="budgets-page">
    <div class="page-header">
      <h2 class="page-title">Cuánto podemos gastar?</h2>
      <div class="month-nav">
        <button class="btn btn-icon" @click="prevMonth">&larr;</button>
        <span class="month-label">{{ monthLabel }}</span>
        <button class="btn btn-icon" @click="nextMonth">&rarr;</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="card">
        <SkeletonLoader variant="text" width="60%" style="margin-bottom: 16px" />
        <SkeletonLoader variant="text" width="100%" style="margin-bottom: 8px" />
        <SkeletonLoader variant="text" width="80%" />
      </div>
      <div class="budgets-grid">
        <SkeletonLoader v-for="n in 3" :key="n" variant="card" />
      </div>
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-sm" @click="loadBudgets">Reintentar</button>
    </div>

    <template v-else>
      <div v-if="statusData" class="summary-card card card-hover">
        <h3 class="card-title">Resumen del mes</h3>
        <div class="summary-row">
          <span>Podemos gastar</span>
          <span class="summary-value">${{ fmt(statusData.total_budgeted) }}</span>
        </div>
        <div class="summary-row">
          <span>Ya gastamos</span>
          <span class="summary-value expense">${{ fmt(statusData.total_spent) }}</span>
        </div>
        <div class="summary-row">
          <span>Nos queda</span>
          <span class="summary-value" :class="statusData.total_remaining >= 0 ? 'income' : 'expense'">${{ fmt(statusData.total_remaining) }}</span>
        </div>
      </div>

      <div class="card chart-card card-hover">
        <h3 class="card-title">Comparamos: lo que podemos vs lo que gastamos</h3>
        <ChartCard v-if="chartData" type="bar" :data="chartData" :options="chartOptions" />
        <p v-else class="empty-text">Aún no hay datos para mostrar</p>
      </div>

      <div class="budgets-grid">
        <BudgetCard
          v-for="item in budgetItems"
          :key="item.category"
          :item="item"
          :status-label="statusLabel"
          @edit="openEdit"
          @delete="handleDelete"
        />
        <div v-if="!budgetItems.length" class="empty-state">
          <p>Aún no tenemos presupuestos para este mes</p>
          <p class="empty-hint">Vamos a definir cuánto podemos gastar en cada cosa</p>
        </div>
      </div>

      <div v-if="unbudgetedCategories.length > 0" class="unbudgeted-section">
        <h3 class="card-title">Categorías sin presupuesto</h3>
        <div class="unbudgeted-list">
          <div v-for="cat in unbudgetedCategories" :key="cat.id" class="unbudgeted-item">
            <span>{{ cat.name }}</span>
            <button class="btn btn-sm btn-primary" @click="createBudgetForCategory(cat)">+ Crear presupuesto</button>
          </div>
        </div>
      </div>

      <BudgetForm :categories="categories" :initial-month="month" :initial-year="year" @submit="createBudget" />

      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal">
          <h3 class="modal-title">Editar Presupuesto</h3>
          <form class="form" @submit.prevent="editBudget">
            <div class="form-group">
              <label class="form-label">Monto mensual</label>
              <input v-model.number="editForm.amount" class="form-input" type="number" step="1000" min="0" required>
            </div>
            <div class="form-actions">
              <span v-if="editError" class="form-error">{{ editError }}</span>
              <button class="btn btn-sm" type="button" @click="showEditModal = false">Cancelar</button>
              <button class="btn btn-primary" type="submit" :disabled="editing">
                {{ editing ? 'Guardando...' : 'Guardar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import ChartCard from '@/components/ChartCard.vue'
import { useCurrency } from '@/composables/useCurrency'
import { useBudgets } from '@/composables/useBudgets'
import BudgetCard from '@/components/budgets/BudgetCard.vue'
import BudgetForm from '@/components/budgets/BudgetForm.vue'

const { fmt } = useCurrency()

const {
  loading, error, month, year, monthLabel, statusData, rawBudgets,
  budgetItems, unbudgetedCategories, chartData, chartOptions,
  prevMonth, nextMonth, statusLabel, loadBudgets, loadCategories,
  createBudget, editBudget, deleteBudget,
} = useBudgets()

const showEditModal = ref(false)
const editingBudget = ref(null)
const editForm = reactive({ amount: 0 })
const editError = ref('')
const editing = ref(false)
const categories = ref([])

function openEdit(item) {
  const raw = rawBudgets.value.find(b => b.category === item.category)
  if (!raw) return
  editingBudget.value = raw
  editForm.amount = item.budgeted
  editError.value = ''
  showEditModal.value = true
}

async function handleEditBudget() {
  editing.value = true
  editError.value = ''
  try {
    await editBudget(editingBudget.value.id, editForm.amount)
    showEditModal.value = false
  } catch (e) {
    editError.value = e?.response?.data?.detail || 'Error al actualizar el presupuesto'
  } finally {
    editing.value = false
  }
}

async function handleDelete(item) {
  if (!confirm('¿Eliminar este presupuesto?')) return
  const raw = rawBudgets.value.find(b => b.category === item.category)
  if (raw) await deleteBudget(raw.id)
}

function createBudgetForCategory(category) {
  // This would open the form with pre-selected category
  // For now, just scroll to form
}

onMounted(() => { loadBudgets(); loadCategories() })
</script>

<style scoped>
.budgets-page { max-width: 960px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-xl); }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); }
.month-nav { display: flex; align-items: center; gap: var(--spacing-md); }
.month-label { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-700); min-width: 160px; text-align: center; }
.btn-icon { width: 32px; height: 32px; border-radius: var(--radius-md); border: 1px solid var(--color-neutral-200); background: var(--color-neutral-0); display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.8rem; }
.btn-icon:hover { border-color: var(--color-primary-400); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--spacing-md); }
.summary-row { display: flex; justify-content: space-between; font-size: 0.875rem; color: var(--color-neutral-600); padding: var(--spacing-sm) 0; }
.summary-value { font-weight: 600; color: var(--color-neutral-900); }
.summary-value.income { color: var(--color-success-600); }
.summary-value.expense { color: var(--color-error-600); }
.chart-card { margin-bottom: var(--spacing-md); }
.budgets-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-xl); }
.empty-text { color: var(--color-neutral-400); font-size: 0.875rem; text-align: center; padding: var(--spacing-lg); }
.empty-state { grid-column: 1 / -1; text-align: center; padding: var(--spacing-2xl); color: var(--color-neutral-400); font-size: 0.875rem; }
.empty-hint { font-size: 0.8rem; color: var(--color-neutral-400); margin-top: var(--spacing-xs); }
.unbudgeted-section { margin-bottom: var(--spacing-xl); }
.unbudgeted-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.unbudgeted-item { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-sm) var(--spacing-md); background: var(--color-neutral-50); border-radius: var(--radius-md); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--color-neutral-0); border-radius: var(--radius-lg); padding: var(--spacing-lg); width: 90%; max-width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
.modal-title { font-size: 1rem; font-weight: 600; margin-bottom: var(--spacing-md); }
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }

.form-actions { display: flex; align-items: center; justify-content: flex-end; gap: var(--spacing-md); margin-top: var(--spacing-sm); }
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); background: var(--color-neutral-100); color: var(--color-neutral-700); }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }

@media (max-width: 640px) {
  .budgets-grid {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  .month-nav {
    align-self: center;
  }
  .unbudgeted-item {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>

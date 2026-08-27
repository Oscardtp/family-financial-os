<template>
  <div class="savings-page">
    <div class="page-header">
      <h2 class="page-title">Metas de Ahorro</h2>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="goals-grid">
        <SkeletonLoader v-for="n in 4" :key="n" variant="card" />
      </div>
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-sm" @click="loadData">Reintentar</button>
    </div>

    <template v-else>
      <div v-if="summary" class="summary-card card card-hover">
        <h3 class="card-title">Resumen de Ahorro</h3>
        <div class="summary-stats">
          <div class="summary-stat">
            <span class="stat-label">Tasa de Ahorro</span>
            <span class="stat-value" :class="summary.savings_rate >= 20 ? 'good' : summary.savings_rate >= 10 ? 'ok' : 'low'">
              {{ summary.savings_rate != null ? summary.savings_rate.toFixed(1) + '%' : 'N/A' }}
            </span>
          </div>
          <div class="summary-stat">
            <span class="stat-label">Ingresos del Mes</span>
            <span class="stat-value">${{ fmt(summary.monthly_income) }}</span>
          </div>
          <div class="summary-stat">
            <span class="stat-label">Gastos del Mes</span>
            <span class="stat-value expense">${{ fmt(summary.monthly_expenses) }}</span>
          </div>
          <div class="summary-stat">
            <span class="stat-label">Total Ahorrado</span>
            <span class="stat-value income">${{ fmt(summary.total_current) }}</span>
          </div>
        </div>
        <p v-if="summary.savings_rate != null" class="savings-tip">
          <template v-if="summary.savings_rate >= 20">¡Excelente! Estás ahorrando más del 20% de tus ingresos.</template>
          <template v-else-if="summary.savings_rate >= 10">Bien, pero intenta llegar al 20% de ahorro.</template>
          <template v-else>Tu tasa de ahorro es baja. Intenta reducir gastos para ahorrar más.</template>
        </p>
      </div>

      <div class="goals-grid">
        <SavingsGoalCard
          v-for="goal in goals"
          :key="goal.id"
          :goal="goal"
          @contribute="openContribution"
          @edit="openEdit"
          @delete="deleteGoal"
        />
        <div v-if="!goals.length" class="empty-state">
          <p>No tienes metas de ahorro todavía</p>
        </div>
      </div>

      <SavingsCreateForm @created="loadData" />
    </template>

    <SavingsEditModal
      :show="showEditModal"
      :goal="editGoalData"
      @close="showEditModal = false"
      @saved="loadData"
    />

    <SavingsContributionModal
      :show="showContributionModal"
      :goal="contributionGoal"
      @close="showContributionModal = false"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { useCurrency } from '@/composables/useCurrency'
import SavingsGoalCard from '@/components/savings/SavingsGoalCard.vue'
import SavingsCreateForm from '@/components/savings/SavingsCreateForm.vue'
import SavingsEditModal from '@/components/savings/SavingsEditModal.vue'
import SavingsContributionModal from '@/components/savings/SavingsContributionModal.vue'

const { fmt } = useCurrency()

const goals = ref([])
const summary = ref(null)
const loading = ref(true)
const error = ref('')

const showContributionModal = ref(false)
const contributionGoal = ref(null)

const showEditModal = ref(false)
const editGoalData = ref(null)

function openContribution(goal) {
  contributionGoal.value = goal
  showContributionModal.value = true
}

function openEdit(goal) {
  editGoalData.value = goal
  showEditModal.value = true
}

async function deleteGoal(id) {
  if (!confirm('¿Eliminar esta meta de ahorro?')) return
  try {
    await api.delete(`/savings/goals/${id}`)
    await loadData()
  } catch (e) {
    console.error(e)
  }
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [goalsRes, summaryRes] = await Promise.all([
      api.get('/savings/goals'),
      api.get('/savings/summary'),
    ])
    goals.value = goalsRes.data
    summary.value = summaryRes.data
  } catch {
    error.value = 'Error al cargar las metas'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.savings-page { max-width: 960px; margin: 0 auto; }
.page-header { margin-bottom: var(--spacing-xl); }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); }
.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}
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
.summary-card { margin-bottom: var(--spacing-xl); }
.summary-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-md); margin-bottom: var(--spacing-md); }
.summary-stat { text-align: center; }
.stat-label { display: block; font-size: 0.75rem; color: var(--color-neutral-500); margin-bottom: 2px; }
.stat-value { display: block; font-size: 1.1rem; font-weight: 700; color: var(--color-neutral-900); }
.stat-value.good { color: var(--color-success-600); }
.stat-value.ok { color: var(--color-warning-600); }
.stat-value.low { color: var(--color-error-600); }
.stat-value.expense { color: var(--color-error-600); }
.stat-value.income { color: var(--color-success-600); }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); background: var(--color-neutral-100); color: var(--color-neutral-700); }

@media (max-width: 640px) {
  .savings-page { padding: 0; }
  .summary-stats { grid-template-columns: 1fr 1fr; }
  .goals-grid { grid-template-columns: 1fr; }
}
</style>

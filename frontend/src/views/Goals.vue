<template>
  <div class="goals-page">
    <div class="page-header">
      <h2 class="page-title">Mis Metas</h2>
      <button class="btn btn-primary" @click="showCreateModal = true">
        + Nueva Meta
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <SkeletonLoader v-for="n in 2" :key="n" variant="card" />
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-sm" @click="loadData">Reintentar</button>
    </div>

    <template v-else>
      <div class="summary-hero card">
        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-value">{{ activeGoals.length }}</span>
            <span class="stat-label">activas</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${{ fmt(totalCurrent) }}</span>
            <span class="stat-label">acumulado</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${{ fmt(totalTarget) }}</span>
            <span class="stat-label">objetivo</span>
          </div>
        </div>
        <div class="summary-bar-track">
          <div class="summary-bar-fill" :style="{ width: `${overallProgress}%` }"></div>
        </div>
        <span class="summary-pct">{{ overallProgress }}% de tu meta total</span>
      </div>

      <div v-if="activeGoals.length === 0" class="empty-state">
        <Target :size="48" class="empty-icon" />
        <p class="empty-text">Todavía no tienes metas</p>
        <p class="empty-hint">Crea tu primera meta y empieza a ahorrar</p>
        <button class="btn btn-primary empty-cta" @click="showCreateModal = true">
          + Crear mi primera meta
        </button>
      </div>

      <GoalFilters
        v-if="activeGoals.length > 0"
        :model-filter-type="filterType"
        :model-sort-by="sortBy"
        @update:model-filter-type="filterType = $event"
        @update:model-sort-by="sortBy = $event"
      />

      <div class="goals-list">
        <GoalCard
          v-for="goal in activeGoals"
          :key="goal.id"
          :goal="goal"
          :expanded="expandedGoal?.id === goal.id"
          :highlighted="highlightedGoalId === goal.id"
          @toggle-expand="toggleDetails"
          @contribute="openContribution"
          @edit="openEditModal"
          @delete="confirmDelete"
        />
      </div>

      <div v-if="completedGoals.length" class="completed-section">
        <h3 class="section-title">Completadas</h3>
        <div class="goals-list">
          <GoalCard
            v-for="goal in completedGoals"
            :key="goal.id"
            :goal="goal"
            completed
          />
        </div>
      </div>
    </template>

    <GoalContributionModal
      :show="showContributionModal"
      :goal="selectedGoal"
      v-model:amount="contributionAmount"
      v-model:date="contributionDate"
      :submitting="contributing"
      @close="closeContribution"
      @submit="submitContribution"
    />

    <GoalCreateModal
      :show="showCreateModal"
      :submitting="creating"
      @close="showCreateModal = false"
      @submit="handleCreateGoal"
    />

    <GoalEditModal
      :show="showEditModal"
      :goal="editingGoal"
      :submitting="editing"
      @close="closeEditModal"
      @submit="handleEditGoal"
    />

    <GoalDeleteConfirm
      :show="showDeleteConfirm"
      :goal="deletingGoal"
      :deleting="deleting"
      @close="showDeleteConfirm = false"
      @confirm="submitDeleteGoal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Target } from 'lucide-vue-next'
import { useGoals } from '@/composables/useGoals'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import GoalCard from '@/components/goals/GoalCard.vue'
import GoalFilters from '@/components/goals/GoalFilters.vue'
import GoalContributionModal from '@/components/goals/GoalContributionModal.vue'
import GoalCreateModal from '@/components/goals/GoalCreateModal.vue'
import GoalEditModal from '@/components/goals/GoalEditModal.vue'
import GoalDeleteConfirm from '@/components/goals/GoalDeleteConfirm.vue'

const {
  goals, loading, error, expandedGoal, highlightedGoalId,
  filterType, sortBy,
  activeGoals, completedGoals, totalCurrent, totalTarget, overallProgress,
  loadData, createGoal, editGoal, deleteGoal, contributeGoal, loadGoalHistory,
  fmt,
} = useGoals()

const showContributionModal = ref(false)
const selectedGoal = ref(null)
const contributionAmount = ref('')
const contributionDate = ref(new Date().toISOString().split('T')[0])
const contributing = ref(false)

const showCreateModal = ref(false)
const creating = ref(false)

const showEditModal = ref(false)
const editingGoal = ref(null)
const editing = ref(false)

const showDeleteConfirm = ref(false)
const deletingGoal = ref(null)
const deleting = ref(false)

function openContribution(goal) {
  selectedGoal.value = goal
  contributionAmount.value = ''
  contributionDate.value = new Date().toISOString().split('T')[0]
  showContributionModal.value = true
}

function closeContribution() {
  showContributionModal.value = false
  selectedGoal.value = null
}

async function submitContribution() {
  if (!selectedGoal.value || !contributionAmount.value) return
  contributing.value = true
  const { error: err } = await contributeGoal(selectedGoal.value.id, contributionAmount.value, contributionDate.value)
  contributing.value = false
  if (err) {
    window.$toast?.error(err)
  } else {
    closeContribution()
    window.$toast?.success('Aporte registrado')
  }
}

async function handleCreateGoal(data) {
  creating.value = true
  const { error: err } = await createGoal(data)
  creating.value = false
  if (err) {
    window.$toast?.error(err)
  } else {
    showCreateModal.value = false
    window.$toast?.success('Meta creada')
    highlightNewGoal()
  }
}

function openEditModal(goal) {
  editingGoal.value = goal
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editingGoal.value = null
}

async function handleEditGoal(data) {
  if (!editingGoal.value) return
  editing.value = true
  const { error: err } = await editGoal(editingGoal.value.id, data)
  editing.value = false
  if (err) {
    window.$toast?.error(err)
  } else {
    closeEditModal()
    window.$toast?.success('Meta actualizada')
  }
}

function confirmDelete(goal) {
  deletingGoal.value = goal
  showDeleteConfirm.value = true
}

async function submitDeleteGoal() {
  if (!deletingGoal.value) return
  deleting.value = true
  const { error: err } = await deleteGoal(deletingGoal.value.id)
  deleting.value = false
  if (err) {
    window.$toast?.error(err)
  } else {
    showDeleteConfirm.value = false
    deletingGoal.value = null
    window.$toast?.success('Meta eliminada')
  }
}

function toggleDetails(goal) {
  if (expandedGoal.value?.id === goal.id) {
    expandedGoal.value = null
  } else {
    expandedGoal.value = goal
    if (!goal.history) loadGoalHistory(goal)
  }
}

function highlightNewGoal() {
  const prevIds = goals.value.map(g => g.id)
  loadData().then(() => {
    const newGoal = goals.value.find(g => !prevIds.includes(g.id))
    if (newGoal) {
      highlightedGoalId.value = newGoal.id
      setTimeout(() => {
        const el = document.querySelector(`[data-goal-id="${newGoal.id}"]`)
        el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 100)
      setTimeout(() => { highlightedGoalId.value = null }, 2000)
    }
  })
}

function handleGoalCreated() {
  highlightNewGoal()
}

onMounted(() => {
  loadData()
  window.addEventListener('goal-created', handleGoalCreated)
})

onUnmounted(() => {
  window.removeEventListener('goal-created', handleGoalCreated)
})
</script>

<style scoped>
.goals-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.summary-hero {
  text-align: center;
  padding: 24px;
  margin-bottom: 24px;
  background: var(--color-surface-tinted-blue);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-lg);
}

.summary-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-neutral-900);
  font-family: var(--font-mono);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-neutral-500);
  text-transform: uppercase;
}

.summary-bar-track {
  height: 8px;
  background: var(--color-neutral-200);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.summary-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-400));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.summary-pct {
  font-size: 0.8125rem;
  color: var(--color-neutral-500);
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.completed-section {
  margin-top: 32px;
}

.empty-cta {
  margin-top: 8px;
}

.btn-primary {
  background: var(--color-primary-500);
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--color-primary-600);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
</style>

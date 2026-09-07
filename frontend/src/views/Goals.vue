<template>
  <div class="goals-page">
    <div class="page-header">
      <h2 class="page-title">
        Mis Metas
      </h2>
      <button
        class="btn btn-primary"
        @click="showCreateModal = true"
      >
        + Nueva Meta
      </button>
    </div>

    <div
      v-if="loading"
      class="loading-state"
    >
      <SkeletonLoader
        v-for="n in 2"
        :key="n"
        variant="card"
      />
    </div>

    <div
      v-else-if="error"
      class="error-state"
    >
      <span>{{ error }}</span>
      <button
        class="btn btn-sm"
        @click="goalsStore.fetchGoals"
      >
        Reintentar
      </button>
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
          <div
            class="summary-bar-fill"
            :style="{ width: `${overallProgress}%` }"
          />
        </div>
        <span class="summary-pct">{{ overallProgress }}% de tu meta total</span>
      </div>

      <GoalFilters
        v-show="goalsStore.goals.length > 0"
        :model-filter-type="filterType"
        :model-sort-by="sortBy"
        @update:model-filter-type="filterType = $event"
        @update:model-sort-by="sortBy = $event"
      />

      <div
        v-if="activeGoals.length === 0 && goalsStore.goals.length === 0"
        class="empty-state"
      >
        <Target
          :size="48"
          class="empty-icon"
        />
        <p class="empty-text">
          Todavía no tienes metas
        </p>
        <p class="empty-hint">
          Crea tu primera meta y empieza a ahorrar
        </p>
        <button
          class="btn btn-primary empty-cta"
          @click="showCreateModal = true"
        >
          + Crear mi primera meta
        </button>
      </div>

      <div
        v-else-if="activeGoals.length === 0 && goalsStore.goals.length > 0"
        class="empty-state"
      >
        <Target
          :size="48"
          class="empty-icon"
        />
        <p class="empty-text">
          No hay metas con este filtro
        </p>
        <p class="empty-hint">
          Prueba con otro filtro o crea una nueva meta
        </p>
      </div>

      <div class="goals-list">
        <GoalCard
          v-for="goal in activeGoals"
          :key="goal.id"
          :goal="goal"
          :expanded="expandedGoal === goal.id"
          :highlighted="highlightedGoalId === goal.id"
          @toggle-expand="goalsStore.toggleDetails(goal)"
          @contribute="goalsStore.openContribution(goal)"
          @edit="goalsStore.openEdit(goal)"
          @delete="goalsStore.confirmDelete(goal)"
        />
      </div>

      <div
        v-if="completedGoals.length"
        class="completed-section"
      >
        <h3 class="section-title">
          Completadas
        </h3>
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
      v-model:amount="contributionAmount"
      v-model:date="contributionDate"
      :show="goalsStore.contributionGoalId !== null"
      :goal="goalsStore.goals.find(g => g.id === goalsStore.contributionGoalId) || null"
      :submitting="goalsStore.isContributing"
      @close="goalsStore.closeContribution"
      @submit="submitContribution"
    />

    <GoalCreateModal
      :show="showCreateModal"
      :submitting="creating"
      @close="showCreateModal = false"
      @submit="handleCreateGoal"
    />

    <GoalEditModal
      :show="goalsStore.editingGoalId !== null"
      :goal="goalsStore.goals.find(g => g.id === goalsStore.editingGoalId) || null"
      :submitting="goalsStore.isEditing"
      @close="goalsStore.closeEdit"
      @submit="submitEdit"
    />

    <GoalDeleteConfirm
      :show="goalsStore.deletingGoalId !== null"
      :goal="goalsStore.goals.find(g => g.id === goalsStore.deletingGoalId) || null"
      :deleting="goalsStore.isDeleting"
      @close="goalsStore.closeDelete"
      @confirm="submitDeleteGoal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { Target } from 'lucide-vue-next'
import { useGoalsStore } from '@/stores/goals'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import GoalCard from '@/components/goals/GoalCard.vue'
import GoalFilters from '@/components/goals/GoalFilters.vue'
import GoalContributionModal from '@/components/goals/GoalContributionModal.vue'
import GoalCreateModal from '@/components/goals/GoalCreateModal.vue'
import GoalEditModal from '@/components/goals/GoalEditModal.vue'
import GoalDeleteConfirm from '@/components/goals/GoalDeleteConfirm.vue'

const goalsStore = useGoalsStore()
const {
  loading, error, expandedGoal, highlightedGoalId,
  filterType, sortBy,
  activeGoals, completedGoals, totalCurrent, totalTarget, overallProgress,
} = storeToRefs(goalsStore)

const { fmt } = goalsStore

const contributionAmount = ref('')
const contributionDate = ref(new Date().toISOString().split('T')[0])
const creating = ref(false)
const showCreateModal = ref(false)

async function submitContribution() {
  const { error: err } = await goalsStore.submitContribution(contributionAmount.value, contributionDate.value)
  if (err) {
    window.$toast?.error(err)
  } else {
    contributionAmount.value = ''
    contributionDate.value = new Date().toISOString().split('T')[0]
    window.$toast?.success('Aporte registrado')
  }
}

async function handleCreateGoal(data) {
  creating.value = true
  const { error: err } = await goalsStore.createGoal(data)
  creating.value = false
  if (err) {
    window.$toast?.error(err)
  } else {
    showCreateModal.value = false
    window.$toast?.success('Meta creada')
  }
}

async function submitEdit(data) {
  const { error: err } = await goalsStore.submitEdit(data)
  if (err) {
    window.$toast?.error(err)
  } else {
    window.$toast?.success('Meta actualizada')
  }
}

async function submitDeleteGoal() {
  const { error: err } = await goalsStore.submitDelete()
  if (err) {
    window.$toast?.error(err)
  } else {
    window.$toast?.success('Meta eliminada')
  }
}

onMounted(() => {
  goalsStore.fetchGoals()
})
</script>

<style scoped>
.goals-page {
  padding-bottom: 80px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.summary-hero {
  margin-bottom: 20px;
}

.summary-stats {
  display: flex;
  justify-content: space-around;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.completed-section {
  margin-top: 32px;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .summary-stats {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
  }

  .stat-item {
    flex: 1 1 30%;
    min-width: 80px;
  }
}
</style>


<template>
  <div class="budget-card card">
    <!-- FASE 6.2: Budget Method — Configuración financiera del hogar
         Próximo: Mostrar distribución needs/wants/savings según método seleccionado.
         Extensión: Agregar sección de análisis de método presupuestal.
         No implementar hasta que backend exponga GET /budget-method -->

    <div v-if="loading" class="bc-skeleton">
      <SkeletonLoader variant="text" width="60%" height="18px" />
      <SkeletonLoader variant="text" width="100%" height="12px" />
      <SkeletonLoader variant="text" width="80%" height="12px" />
    </div>

    <div v-else-if="error" class="bc-error">
      <span class="bc-error-text">No pudimos cargar tu presupuesto.</span>
    </div>

    <template v-else>
      <div v-if="isEmpty" class="bc-empty">
        <p class="bc-empty-text">Aun no has configurado un presupuesto.</p>
        <button class="bc-empty-cta" @click="$emit('open-budget')">
          Crear presupuesto
        </button>
      </div>

      <div v-else class="bc-card-content">
        <div class="bc-header">
          <h3 class="bc-title">Presupuesto</h3>
          <StatusBadge
            v-if="globalStatus !== 'ok'"
            class="bc-status-badge"
            :label="globalStatusLabel"
            :variant="statusVariant"
          />
        </div>

        <div class="bc-amounts">
          <span class="bc-spent">${{ fmt(projection.total_projected_spent) }}</span>
          <span class="bc-separator"> / </span>
          <span class="bc-total">${{ fmt(projection.total_budgeted) }}</span>
        </div>

        <div class="bc-bar-track">
          <div
            class="bc-bar-fill"
            :class="barClass"
            :style="{ width: barWidth + '%' }"
          />
        </div>

        <div v-if="atRiskCategories.length" class="bc-risk-list">
          <div v-for="cat in atRiskCategories" :key="cat.category" class="bc-risk-item">
            <span class="bc-risk-name">{{ cat.category }}</span>
            <span class="bc-risk-message">{{ cat.message }}</span>
          </div>
        </div>

        <button class="bc-cta" @click="$emit('open-budget')">
          Ver todo el presupuesto
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  budgetStatus: {
    type: Array,
    default: () => [],
  },
  budgetProjection: {
    type: Object,
    default: () => ({
      total_projected_spent: 0,
      total_budgeted: 0,
      total_will_exceed: false,
    }),
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
})

defineEmits(['open-budget'])

const projection = computed(() => props.budgetProjection)

const isEmpty = computed(() => {
  return (
    !props.budgetStatus.length ||
    projection.value.total_budgeted === 0
  )
})

const atRiskCategories = computed(() => {
  return props.budgetStatus
    .filter((item) => item.status !== 'ok')
    .slice(0, 2)
})

const globalStatus = computed(() => {
  if (atRiskCategories.value.length === 0) return 'ok'
  const hasExceeded = atRiskCategories.value.some(
    (c) => c.status === 'exceeded' || c.status === 'over'
  )
  if (hasExceeded) return 'exceeded'
  return 'warning'
})

const globalStatusLabel = computed(() => {
  const map = {
    ok: 'Vamos bien',
    warning: 'Cuidado',
    exceeded: 'Nos pasamos',
  }
  return map[globalStatus.value] || 'Vamos bien'
})

const statusVariant = computed(() => {
  const map = { ok: 'success', warning: 'warning', exceeded: 'error' }
  return map[globalStatus.value] || 'default'
})

const barWidth = computed(() => {
  const spent = projection.value.total_projected_spent || 0
  const budgeted = projection.value.total_budgeted || 0
  if (budgeted === 0) return 0
  return Math.min((spent / budgeted) * 100, 100)
})

const barClass = computed(() => {
  const status = globalStatus.value
  if (status === 'exceeded') return 'bc-bar-fill--danger'
  if (status === 'warning') return 'bc-bar-fill--warning'
  return 'bc-bar-fill--primary'
})
</script>

<style scoped>
.budget-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-neutral-100);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.bc-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.bc-error {
  text-align: center;
  padding: var(--spacing-md);
}

.bc-error-text {
  font-size: var(--font-size-sm);
  color: var(--color-error-500);
}

.bc-empty {
  text-align: center;
  padding: var(--spacing-md) 0;
}

.bc-empty-text {
  font-size: var(--font-size-sm);
  color: var(--color-neutral-500);
  margin: 0 0 var(--spacing-md);
}

.bc-empty-cta {
  background: var(--color-primary-600);
  color: var(--color-neutral-0);
  border: none;
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--font-size-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast);
}

.bc-empty-cta:hover {
  background: var(--color-primary-700);
}

.bc-empty-cta:active {
  transform: scale(0.97);
}

.bc-card-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.bc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bc-title {
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-neutral-900);
}

.bc-amounts {
  font-family: var(--font-mono);
  font-size: 1.4rem;
  font-weight: 700;
}

.bc-spent {
  color: var(--color-neutral-900);
}

.bc-separator {
  color: var(--color-neutral-400);
  font-weight: 400;
}

.bc-total {
  color: var(--color-neutral-500);
  font-weight: 500;
}

.bc-bar-track {
  height: 8px;
  background: var(--color-neutral-100);
  border-radius: 4px;
  overflow: hidden;
}

.bc-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width var(--transition-slow);
}

.bc-bar-fill--primary {
  background: var(--color-primary-500);
}

.bc-bar-fill--warning {
  background: var(--color-warning-500);
}

.bc-bar-fill--danger {
  background: var(--color-error-500);
}

.bc-risk-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.bc-risk-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm);
  background: var(--color-neutral-50);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
}

.bc-risk-name {
  font-weight: 500;
  color: var(--color-neutral-700);
}

.bc-risk-message {
  color: var(--color-neutral-500);
  text-align: right;
  max-width: 55%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bc-cta {
  align-self: flex-start;
  background: none;
  border: none;
  color: var(--color-primary-600);
  font-size: var(--font-size-sm);
  font-weight: 600;
  cursor: pointer;
  padding: var(--spacing-xs) 0;
  transition: color var(--transition-fast);
}

.bc-cta:hover {
  color: var(--color-primary-700);
  text-decoration: underline;
}

.bc-cta:active {
  opacity: 0.7;
}
</style>

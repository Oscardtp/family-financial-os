<template>
  <div
    :data-goal-id="goal.id"
    class="goal-card card"
    :class="{ expanded: expanded, 'highlight-new': highlighted, completed: completed }"
  >
    <div class="goal-header">
      <span class="goal-icon">{{ goal.goal_type === 'investment' ? '📈' : '🎯' }}</span>
      <div class="goal-title">
        <h3 class="goal-name">{{ goal.name }}</h3>
        <span class="goal-badges">
          <span class="goal-type-badge" :class="completed ? 'completed' : goal.goal_type">
            {{ completed ? 'Lograda' : goal.goal_type === 'investment' ? 'Inversión' : 'Ahorro' }}
          </span>
          <span v-if="!completed && goal.priority" class="priority-badge" :class="goal.priority">
            {{ goal.priority === 'high' ? 'Alta' : goal.priority === 'medium' ? 'Media' : 'Baja' }}
          </span>
        </span>
      </div>
    </div>

    <template v-if="!completed">
      <div class="goal-amounts">
        <div class="amount-row amount-row-primary">
          <span class="amount-label">Tienes</span>
          <span class="amount-current">${{ fmt(goal.current_amount) }}</span>
        </div>
        <div class="amount-row amount-row-primary">
          <span class="amount-label">Necesitas</span>
          <span class="amount-target">${{ fmt(goal.target_amount) }}</span>
        </div>
        <div class="amount-row amount-row-remaining">
          <span class="amount-label">Faltan</span>
          <span class="amount-remaining">${{ fmt((Number(goal.target_amount) || 0) - (Number(goal.current_amount) || 0)) }}</span>
        </div>
      </div>

      <div class="goal-progress">
        <div class="progress-bar-track">
          <div class="progress-bar-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <span class="progress-pct">{{ progress }}%</span>
      </div>

      <div v-if="goal.monthly_contribution" class="goal-monthly">
        <span class="monthly-label">Aporte mensual:</span>
        <span class="monthly-value">${{ fmt(goal.monthly_contribution) }}</span>
      </div>

      <div v-if="goal.target_date" class="goal-timeline">
        <Calendar :size="14" />
        <span>Para: {{ fmtMonth(goal.target_date) }}</span>
        <span v-if="monthsLeft" class="months-remaining">
          ({{ monthsLeft }} meses)
        </span>
      </div>

      <div v-if="goal.goal_type === 'investment' && goal.expected_return_rate" class="goal-projection">
        <div class="projection-header">
          <TrendingUp :size="14" />
          <span>Proyección</span>
        </div>
        <div class="projection-details">
          <span>Rendimiento: {{ goal.expected_return_rate }}% EA</span>
          <span v-if="goal.horizon_months">Horizonte: {{ goal.horizon_months }} meses</span>
        </div>
        <div v-if="goal.projected_value" class="projection-result">
          <span class="projection-label">Valor proyectado:</span>
          <span class="projection-amount">${{ fmt(goal.projected_value) }}</span>
        </div>
      </div>

      <div class="goal-actions">
        <button class="action-btn primary" @click="$emit('contribute', goal)">
          + Aportar
        </button>
        <button class="action-btn secondary" @click="$emit('toggle-expand', goal)">
          {{ expanded ? 'Cerrar' : 'Ver detalles' }}
        </button>
      </div>

      <div v-if="expanded" class="goal-expanded">
        <div class="expanded-section">
          <div class="expanded-actions">
            <button class="expanded-btn" @click="$emit('edit', goal)">
              ✏️ Editar
            </button>
            <button class="expanded-btn danger" @click="$emit('delete', goal)">
              🗑️ Eliminar
            </button>
          </div>
        </div>
        <div v-if="goal.history?.length" class="expanded-section">
          <h4 class="expanded-title">Historial de aportes</h4>
          <div class="history-list">
            <div v-for="entry in goal.history" :key="entry.id" class="history-item">
              <span class="history-date">{{ fmtMonth(entry.contribution_date) }}</span>
              <span class="history-amount">${{ fmt(entry.amount) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="expanded-section">
          <p class="expanded-empty">Aún no hay aportes registrados</p>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="completed-details">
        <span class="completed-amount">${{ fmt(goal.target_amount) }} ahorrados</span>
        <span v-if="goal.target_date" class="completed-date">Meta: {{ fmtMonth(goal.target_date) }}</span>
      </div>
      <div class="goal-progress">
        <div class="progress-bar-track">
          <div class="progress-bar-fill full"></div>
        </div>
        <span class="progress-pct">100%</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Calendar, TrendingUp } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import { useFinancialHelpers } from '@/composables/useFinancialHelpers'

const { fmt, fmtMonth } = useCurrency()
const { calcPercentage } = useFinancialHelpers()

const props = defineProps({
  goal: { type: Object, required: true },
  expanded: { type: Boolean, default: false },
  highlighted: { type: Boolean, default: false },
  completed: { type: Boolean, default: false },
})

defineEmits(['toggle-expand', 'contribute', 'edit', 'delete'])

const progress = computed(() => {
  if (!props.goal.target_amount) return 0
  return calcPercentage(props.goal.current_amount, props.goal.target_amount)
})

const monthsLeft = computed(() => {
  if (!props.goal.target_date) return null
  const target = new Date(props.goal.target_date)
  const now = new Date()
  const months = (target.getFullYear() - now.getFullYear()) * 12 + (target.getMonth() - now.getMonth())
  return months > 0 ? months : null
})
</script>
<style scoped>
.goal-card {
  padding: 20px;
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
  border-left: 3px solid var(--color-primary-400);
}

.goal-card.highlight-new {
  animation: highlightPulse 2s ease;
  border-left-color: var(--color-success-400);
  box-shadow: 0 0 0 3px var(--color-success-100), var(--shadow-md);
}

@keyframes highlightPulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 var(--color-success-200); }
  25% { transform: scale(1.02); box-shadow: 0 0 0 8px var(--color-success-100); }
  50% { transform: scale(1); box-shadow: 0 0 0 4px var(--color-success-50); }
  100% { transform: scale(1); box-shadow: none; }
}

.goal-card.expanded {
  box-shadow: var(--shadow-md);
}

.goal-card.completed {
  opacity: 0.7;
}

.goal-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.goal-icon {
  font-size: 24px;
  line-height: 1;
}

.goal-title {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.goal-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.goal-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-neutral-800);
  line-height: 1.3;
}

.goal-type-badge {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 9999px;
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

.goal-type-badge.investment {
  background: var(--color-info-100);
  color: var(--color-info-700);
}

.goal-type-badge.completed {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.priority-badge {
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 9999px;
}

.priority-badge.high {
  background: var(--color-error-50);
  color: var(--color-error-600);
}

.priority-badge.medium {
  background: var(--color-warning-50);
  color: var(--color-warning-600);
}

.priority-badge.low {
  background: var(--color-neutral-100);
  color: var(--color-neutral-600);
}

.goal-amounts {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.amount-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount-row-remaining {
  padding-top: 8px;
  margin-top: 4px;
  border-top: 1px solid var(--color-neutral-100);
}

.amount-label {
  font-size: 0.875rem;
  color: var(--color-neutral-500);
}

.amount-current {
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-success-600);
}

.amount-target {
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-neutral-700);
}

.amount-remaining {
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-error-600);
}

@media (max-width: 640px) {
  .goal-card {
    padding: 16px;
  }

  .goal-icon {
    font-size: 20px;
  }

  .goal-amounts {
    gap: 10px;
  }

  .amount-row {
    padding: 6px 0;
  }

  .goal-actions {
    flex-direction: column;
  }

  .goal-actions .action-btn {
    width: 100%;
  }

  .expanded-actions {
    flex-direction: column;
  }

  .expanded-btn {
    width: 100%;
    text-align: center;
  }
}
</style>

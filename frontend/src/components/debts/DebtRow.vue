<template>
  <div class="debt-row" :class="{ 'is-expanded': isExpanded }">
    <div class="debt-main" @click="$emit('toggle-expand', debt.id)">
      <div class="debt-left">
        <button class="expand-btn" :class="{ expanded: isExpanded }">
          <ChevronRight :size="16" />
        </button>
        <div class="debt-identity">
          <div class="debt-name">{{ debt.name }}</div>
          <div class="debt-creditor">{{ debt.creditor }}</div>
        </div>
        <span class="status-badge" :class="statusClass">{{ statusLabel }}</span>
      </div>
      <div class="debt-right">
        <div class="debt-amounts">
          <div class="debt-balance">${{ fmt(debt.current_balance) }}</div>
          <div class="debt-min">Min: ${{ fmt(debt.minimum_payment) }}</div>
        </div>
        <div class="debt-due">
          <div class="due-day" :class="dueClass">Día {{ debt.due_day }}</div>
          <div class="due-month">{{ currentMonthShort }}</div>
        </div>
        <div class="debt-interest">{{ debt.interest_rate }}%</div>
      </div>
    </div>

    <Transition name="expand">
      <div v-if="isExpanded" class="debt-expanded">
        <DebtExpandedPanel
          :debt="debt"
          @edit="$emit('edit', $event)"
          @pay="$emit('pay', $event)"
          @amortization="$emit('amortization', $event)"
          @deactivate="$emit('deactivate', $event)"
          @activate="$emit('activate', $event)"
          @reactivate="$emit('reactivate', $event)"
          @request-delete="$emit('request-delete', $event)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronRight } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import DebtExpandedPanel from './DebtExpandedPanel.vue'

const { fmt } = useCurrency()

const props = defineProps({
  debt: { type: Object, required: true },
  isExpanded: { type: Boolean, default: false },
})

defineEmits(['toggle-expand', 'edit', 'pay', 'amortization', 'deactivate', 'activate', 'reactivate', 'request-delete'])

const currentMonthShort = computed(() =>
  new Date().toLocaleString('es-CO', { month: 'short' }).toUpperCase()
)

const statusClass = computed(() => {
  const map = { active: 'status-active', paused: 'status-paused', paid_off: 'status-paid' }
  return map[props.debt.status] || 'status-active'
})

const statusLabel = computed(() => {
  const map = { active: 'Activa', paused: 'Pausada', paid_off: 'Pagada' }
  return map[props.debt.status] || 'Activa'
})

const dueClass = computed(() => {
  if (props.debt.status !== 'active') return ''
  const today = new Date().getDate()
  if (props.debt.due_day <= today + 2) return 'due-soon'
  return ''
})
</script>

<style scoped>
.debt-row {
  border-bottom: 1px solid var(--color-neutral-100);
  transition: background var(--transition-fast);
}

.debt-row:hover {
  background: var(--color-neutral-50);
}

.debt-row.is-expanded {
  background: var(--color-primary-50);
  border-bottom-color: var(--color-primary-100);
}

.debt-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  gap: var(--spacing-md);
}

.debt-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 1;
  min-width: 0;
}

.expand-btn {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  color: var(--color-neutral-400);
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}

.expand-btn.expanded {
  transform: rotate(90deg);
}

.debt-identity {
  min-width: 0;
}

.debt-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-neutral-800);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.debt-creditor {
  font-size: 12px;
  color: var(--color-neutral-500);
}

.status-badge {
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  flex-shrink: 0;
}

.status-active {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.status-paused {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.status-paid {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

.debt-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  flex-shrink: 0;
}

.debt-amounts {
  text-align: right;
}

.debt-balance {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 14px;
  color: var(--color-neutral-800);
}

.debt-min {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-neutral-500);
}

.debt-due {
  text-align: center;
  min-width: 40px;
}

.due-day {
  font-weight: 700;
  font-size: 16px;
  color: var(--color-neutral-700);
  line-height: 1;
}

.due-day.due-soon {
  color: var(--color-warning-600);
}

.due-month {
  font-size: 10px;
  color: var(--color-neutral-400);
  text-transform: uppercase;
}

.debt-interest {
  font-size: 12px;
  color: var(--color-neutral-500);
  min-width: 35px;
  text-align: right;
}

.debt-expanded {
  padding: 0 var(--spacing-md) var(--spacing-md);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 200ms ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

@media (max-width: 640px) {
  .debt-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .debt-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style>

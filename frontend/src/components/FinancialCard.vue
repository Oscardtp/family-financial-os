<template>
  <div
    class="financial-card card-hover"
    :class="variant"
  >
    <div class="card-header">
      <div
        class="card-icon"
        :class="variant"
      >
        <slot name="icon">
          <component
            :is="icon"
            v-if="icon"
            :size="20"
          />
        </slot>
      </div>
      <span class="card-label">{{ label }}</span>
    </div>
    <div class="card-value">
      <span
        v-if="showCurrency"
        class="currency"
      >$</span>
      <span class="amount">{{ formattedAmount }}</span>
    </div>
    <div
      v-if="subtitle"
      class="card-subtitle"
      :class="subtitleVariant"
    >
      {{ subtitle }}
    </div>
    <div
      v-if="$slots.footer"
      class="card-footer"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  amount: {
    type: Number,
    required: true
  },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'income', 'expense', 'savings', 'debt', 'net-worth'].includes(v)
  },
  icon: {
    type: [Object, null],
    default: null
  },
  subtitle: {
    type: String,
    default: null
  },
  subtitleVariant: {
    type: String,
    default: 'neutral',
    validator: (v) => ['neutral', 'positive', 'negative', 'warning'].includes(v)
  },
  showCurrency: {
    type: Boolean,
    default: true
  },
  decimals: {
    type: Number,
    default: 0
  }
})

const { fmt } = useCurrency()

const formattedAmount = computed(() => {
  return fmt(props.amount, props.decimals)
})
</script>

<style scoped>
.financial-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-neutral-200);
  border-left: 4px solid var(--color-neutral-300);
}

.financial-card.income {
  border-left-color: var(--color-income);
}

.financial-card.expense {
  border-left-color: var(--color-expense);
}

.financial-card.savings {
  border-left-color: var(--color-transfer);
}

.financial-card.debt {
  border-left-color: var(--color-warning-500);
}

.financial-card.net-worth {
  border-left-color: var(--color-secondary-500);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--color-neutral-100);
  color: var(--color-neutral-600);
}

.card-icon.income {
  background: var(--color-income-bg);
  color: var(--color-income);
}

.card-icon.expense {
  background: var(--color-neutral-100);
  color: var(--color-expense);
}

.card-icon.savings {
  background: var(--color-transfer-bg);
  color: var(--color-transfer);
}

.card-icon.debt {
  background: var(--color-budget-warning-bg);
  color: var(--color-warning-600);
}

.card-icon.net-worth {
  background: var(--color-secondary-100);
  color: var(--color-secondary-600);
}

.card-label {
  font-size: 14px;
  color: var(--color-neutral-500);
  font-weight: 500;
}

.card-value {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.currency {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--color-neutral-500);
}

.amount {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: 700;
  color: var(--color-neutral-900);
  letter-spacing: -0.02em;
}

.card-subtitle {
  margin-top: var(--spacing-xs);
  font-size: 13px;
}

.card-subtitle.positive {
  color: var(--color-success-600);
}

.card-subtitle.negative {
  color: var(--color-error-600);
}

.card-subtitle.warning {
  color: var(--color-warning-600);
}

.card-subtitle.neutral {
  color: var(--color-neutral-500);
}

.card-footer {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-neutral-100);
}

[data-theme="dark"] .financial-card {
  background: var(--color-neutral-100);
  border-color: var(--color-neutral-200);
}

[data-theme="dark"] .card-icon {
  background: var(--color-neutral-200);
}
</style>

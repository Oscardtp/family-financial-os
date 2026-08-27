<template>
  <div class="card card-hover">
    <div v-if="transactions.length" class="tx-list">
      <div v-for="tx in transactions" :key="tx.id" class="tx-item">
        <div class="tx-info">
          <span class="tx-desc">{{ tx.description || 'Sin descripción' }}</span>
          <span class="tx-date">{{ tx.date }}</span>
        </div>
        <span class="tx-amount" :class="tx.type">
          {{ tx.type === 'income' ? '+' : '-' }}${{ fmt(tx.amount) }}
        </span>
        <button class="btn btn-sm btn-danger" @click="$emit('delete', tx.id)">X</button>
      </div>
    </div>
    <p v-else class="empty-text">No hay transacciones con este filtro</p>
  </div>
</template>

<script setup>
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

defineProps({
  transactions: { type: Array, default: () => [] },
})

defineEmits(['delete'])
</script>

<style scoped>
.tx-list { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.tx-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-100);
}
.tx-item:last-child { border-bottom: none; }
.tx-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.tx-desc { font-size: 0.875rem; font-weight: 500; color: var(--color-neutral-800); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tx-date { font-size: 0.7rem; color: var(--color-neutral-400); }
.tx-amount { font-size: 0.875rem; font-weight: 600; font-family: var(--font-mono); }
.tx-amount.income { color: var(--color-success-600); }
.tx-amount.expense { color: var(--color-error-600); }
.empty-text { color: var(--color-neutral-400); font-size: 0.875rem; text-align: center; padding: var(--spacing-lg); }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }
.btn-danger { background: var(--color-error-600); color: white; }
.btn-danger:hover { background: var(--color-error-700); }
</style>

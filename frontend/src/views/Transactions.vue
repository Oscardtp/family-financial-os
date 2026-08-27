<template>
  <div class="transactions-page">
    <div class="page-header">
      <h2 class="page-title">Transacciones</h2>
      <button class="btn btn-sm btn-outline" @click="exportCSV">Exportar movimientos</button>
    </div>

    <div class="filters">
      <button v-for="f in filterOptions" :key="f.value" class="filter-btn" :class="{ active: filter === f.value }" @click="filter = f.value">
        {{ f.label }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="card">
        <SkeletonLoader v-for="n in 5" :key="n" variant="text" style="margin-bottom: 12px" />
      </div>
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-sm" @click="loadData">Reintentar</button>
    </div>

    <template v-else>
      <TransactionList :transactions="filtered" @delete="deleteTransaction" />
      <TransactionForm
        :accounts="accounts"
        :income-categories="incomeCategories"
        :expense-categories="expenseCategories"
        @submit="handleCreate"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { useTransactions } from '@/composables/useTransactions'
import TransactionList from '@/components/transactions/TransactionList.vue'
import TransactionForm from '@/components/transactions/TransactionForm.vue'

const {
  transactions, accounts, categories, loading, error,
  incomeCategories, expenseCategories,
  loadData, createTransaction, deleteTransaction, exportCSV,
} = useTransactions()

const filter = ref('all')

const filterOptions = [
  { label: 'Todas', value: 'all' },
  { label: 'Ingresos', value: 'income' },
  { label: 'Gastos', value: 'expense' },
  { label: 'Transferencias', value: 'transfer' },
]

const filtered = computed(() => {
  if (filter.value === 'all') return transactions.value
  return transactions.value.filter(t => t.type === filter.value)
})

async function handleCreate(payload) {
  await createTransaction(payload)
}

onMounted(loadData)
</script>

<style scoped>
.transactions-page { max-width: 960px; margin: 0 auto; }
.page-header { margin-bottom: var(--spacing-lg); }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); }
.filters { display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-lg); flex-wrap: wrap; }
.filter-btn {
  padding: var(--spacing-xs) var(--spacing-md); border-radius: 999px;
  border: 1px solid var(--color-neutral-200); background: var(--color-neutral-0);
  font-size: 0.8rem; font-weight: 500; color: var(--color-neutral-600); cursor: pointer;
  transition: all 150ms ease;
}
.filter-btn:hover { border-color: var(--color-primary-300); color: var(--color-primary-600); }
.filter-btn.active { background: var(--color-primary-600); color: white; border-color: var(--color-primary-600); }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); background: var(--color-neutral-100); color: var(--color-neutral-700); }
.btn-outline { background: var(--color-neutral-0); border: 1px solid var(--color-neutral-200); color: var(--color-neutral-700); }
.btn-outline:hover { border-color: var(--color-primary-400); color: var(--color-primary-600); }
</style>

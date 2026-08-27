<template>
  <div class="tab-content">
    <div v-for="d in debts" :key="d.debt_id" class="card">
      <h3>{{ d.name }}</h3>
      <div class="debt-grid">
        <div><span class="label">Saldo actual</span><span class="value">${{ fmt(d.current_balance) }}</span></div>
        <div><span class="label">Meses para pagar</span><span class="value">{{ d.months_to_payoff }}</span></div>
        <div><span class="label">Total a pagar</span><span class="value">${{ fmt(d.total_paid) }}</span></div>
        <div><span class="label">Total intereses</span><span class="value expense">${{ fmt(d.total_interest) }}</span></div>
      </div>
    </div>
    <p v-if="!debts?.length" class="empty">Sin deudas registradas</p>
  </div>
</template>

<script setup>
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

defineProps({
  debts: { type: Array, default: () => [] },
})
</script>

<style scoped>
.tab-content { display: flex; flex-direction: column; gap: var(--spacing-md); animation: fadeIn 200ms ease; }
.card h3 { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--spacing-md); }
.debt-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.debt-grid > div { display: flex; flex-direction: column; gap: 2px; }
.label { font-size: 0.75rem; color: var(--color-neutral-500); }
.value { font-size: 0.9rem; font-weight: 600; font-family: var(--font-mono); color: var(--color-neutral-900); }
.value.expense { color: var(--color-error-600); }
.empty { color: var(--color-neutral-400); text-align: center; padding: var(--spacing-lg); font-size: 0.875rem; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>

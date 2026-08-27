<template>
  <div class="projections">
    <div class="tabs">
      <button v-for="tab in tabs" :key="tab.id" class="tab" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">Cargando proyecciones...</div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn-retry" @click="loadData">Reintentar</button>
    </div>

    <div v-else>
      <CashFlowTab v-if="activeTab === 'cashflow'" :cash-flow="cashFlow" :max-val="maxCashFlow" :bar-width="barWidth" />
      <DebtProjectionTab v-if="activeTab === 'debts'" :debts="debtProjections.debts" />
      <SavingsProjectionTab v-if="activeTab === 'savings'" :goals="savingsProjection.goals" />
      <ScenarioSimulator v-if="activeTab === 'scenario'" :form="scenarioForm" :result="scenarioResult" :loading="scenarioLoading" :max-val="maxScenario" :bar-width="barWidth" @run="runScenario" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProjections } from '@/composables/useProjections'
import CashFlowTab from '@/components/projections/CashFlowTab.vue'
import DebtProjectionTab from '@/components/projections/DebtProjectionTab.vue'
import SavingsProjectionTab from '@/components/projections/SavingsProjectionTab.vue'
import ScenarioSimulator from '@/components/projections/ScenarioSimulator.vue'

const {
  loading, error, cashFlow, debtProjections, savingsProjection,
  scenarioResult, scenarioLoading, scenarioForm,
  maxCashFlow, maxScenario, barWidth,
  loadData, runScenario,
} = useProjections()

const tabs = [
  { id: 'cashflow', label: 'Flujo de Caja' },
  { id: 'debts', label: 'Deudas' },
  { id: 'savings', label: 'Ahorro' },
  { id: 'scenario', label: 'Simulador' },
]

const activeTab = ref('cashflow')

onMounted(loadData)
</script>

<style scoped>
.projections { max-width: 960px; margin: 0 auto; }
.tabs {
  display: flex; gap: var(--spacing-xs); margin-bottom: var(--spacing-xl);
  border-bottom: 1px solid var(--color-neutral-200); padding-bottom: var(--spacing-xs);
}
.tab {
  padding: var(--spacing-sm) var(--spacing-md); border: none; background: none;
  font-size: 0.875rem; color: var(--color-neutral-500); cursor: pointer;
  border-radius: var(--radius-md) var(--radius-md) 0 0; transition: all 150ms ease;
}
.tab:hover { color: var(--color-neutral-700); }
.tab.active { color: var(--color-primary-600); border-bottom: 2px solid var(--color-primary-600); font-weight: 500; }
.loading { text-align: center; padding: var(--spacing-2xl); color: var(--color-neutral-400); }
.error-state {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--spacing-md); padding: var(--spacing-2xl);
  color: var(--color-neutral-500); font-size: 0.875rem;
}
.btn-retry {
  padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-primary-600);
  color: white; border: none; border-radius: var(--radius-md);
  font-size: 0.85rem; font-weight: 600; cursor: pointer;
}
.btn-retry:hover { background: var(--color-primary-700); }

@media (max-width: 480px) {
  .tabs {
    flex-wrap: wrap;
    gap: 4px;
  }
  .tab {
    flex: 1;
    min-width: 0;
    text-align: center;
    font-size: 0.75rem;
    padding: var(--spacing-xs) var(--spacing-sm);
  }
}
</style>

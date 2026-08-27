<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="$emit('close')">
        <div class="modal-content modal-wide" @click.stop>
          <div class="modal-header">
            <h3>Tabla de amortización</h3>
            <button class="modal-close" @click="$emit('close')">&times;</button>
          </div>

          <div v-if="amortLoading" class="loading-state">
            <span>Cargando...</span>
          </div>

          <div v-else-if="amortData" class="amort-content">
            <div class="amort-summary">
              <div class="summary-row">
                <span class="summary-label">Deuda</span>
                <span class="summary-value">{{ amortData.debt_name }}</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">Saldo Original</span>
                <span class="summary-value">${{ fmt(amortData.original_balance ?? 0) }}</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">Tasa Mensual</span>
                <span class="summary-value">{{ amortData.interest_rate }}%</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">Pago Mensual</span>
                <span class="summary-value">${{ fmt(amortData.monthly_payment ?? 0) }}</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">Total Intereses</span>
                <span class="summary-value expense">${{ fmt(amortData.total_interest ?? 0) }}</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">Meses para pagar</span>
                <span class="summary-value">{{ amortData.payoff_months }}</span>
              </div>
            </div>

            <div class="amort-table-wrapper">
              <table class="amort-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Pago</th>
                    <th>Capital</th>
                    <th>Interes</th>
                    <th>Saldo</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in visibleRows" :key="idx">
                    <td>{{ row.month }}</td>
                    <td>${{ fmt(row.payment ?? 0) }}</td>
                    <td>${{ fmt(row.principal ?? 0) }}</td>
                    <td>${{ fmt(row.interest ?? 0) }}</td>
                    <td>${{ fmt(row.balance ?? 0) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p v-if="amortData.rows && amortData.rows.length > 24" class="amort-note">
              Mostrando 24 de {{ amortData.rows.length }} cuotas.
            </p>
          </div>

          <div v-else class="empty-state">
            <span>No hay datos de amortización disponibles.</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import api from '@/services/api'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  show: { type: Boolean, default: false },
  debtId: { type: String, default: '' }
})

defineEmits(['close'])

const amortData = ref(null)
const amortLoading = ref(false)

const visibleRows = computed(() => {
  if (!amortData.value?.rows) return []
  return amortData.value.rows.slice(0, 24)
})

watch(
  () => props.show,
  async (val) => {
    if (val && props.debtId) {
      amortLoading.value = true
      amortData.value = null
      try {
        const { data } = await api.get(`/debts/${props.debtId}/amortization`)
        amortData.value = data
      } catch (e) {
        console.error('Error fetching amortization:', e)
      } finally {
        amortLoading.value = false
      }
    }
  }
)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--spacing-md);
}

.modal-content {
  background: var(--color-neutral-0);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.modal-wide {
  max-width: 640px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--color-neutral-900);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-neutral-500);
  line-height: 1;
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--color-neutral-500);
  font-size: 14px;
}

.amort-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-neutral-50);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
}

.summary-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-label {
  font-size: 11px;
  color: var(--color-neutral-500);
  font-weight: 500;
  text-transform: uppercase;
}

.summary-value {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-neutral-800);
}

.summary-value.expense {
  color: var(--color-error-600);
}

.amort-table-wrapper {
  overflow-x: auto;
}

.amort-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.amort-table th {
  text-align: left;
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 2px solid var(--color-neutral-200);
  color: var(--color-neutral-600);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.amort-table td {
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-neutral-100);
  color: var(--color-neutral-700);
  font-family: var(--font-mono);
}

.amort-table tbody tr:hover {
  background: var(--color-neutral-50);
}

.amort-note {
  margin-top: var(--spacing-md);
  font-size: 12px;
  color: var(--color-neutral-500);
  text-align: center;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

[data-theme="dark"] .modal-content {
  background: var(--color-neutral-100);
}

[data-theme="dark"] .amort-summary {
  background: var(--color-neutral-200);
}
</style>
<template>
  <div class="debts-page">
    <div class="page-header">
      <h2 class="page-title">Mis Deudas</h2>
      <button class="btn btn-primary btn-add" @click="showNewDebtModal = true">
        + Nueva Deuda
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="debts-list">
        <SkeletonLoader v-for="n in 3" :key="n" variant="card" />
      </div>
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-sm" @click="loadDebts">Reintentar</button>
    </div>

    <template v-else>
      <div v-if="dueAlerts.length" class="alerts-section">
        <div class="alerts-list">
          <div
            v-for="alert in dueAlerts"
            :key="alert.debt_id + alert.type"
            class="alert-card"
            :class="'alert-' + alert.severity"
          >
            <span class="alert-icon">{{ alert.severity === 'critical' ? '!' : alert.severity === 'warning' ? '~' : 'i' }}</span>
            <span class="alert-message">{{ alert.message }}</span>
          </div>
        </div>
      </div>

      <DebtSummary
        :total-debt="totalDebt"
        :total-monthly="totalMonthlyPayment"
        :active-count="activeDebts.length"
        :next-due="nextDueDay"
      />

      <div class="debts-list">
        <div
          v-for="debt in debts"
          :key="debt.id"
          class="debt-item"
          :class="{ expanded: expandedDebt === debt.id }"
        >
          <DebtRow
            :debt="debt"
            :is-expanded="expandedDebt === debt.id"
            @toggle-expand="toggleDebt"
            @edit="openEdit"
            @pay="openPayment"
            @amortization="openAmortization"
            @deactivate="handleToggleStatus"
            @activate="handleToggleStatus"
            @reactivate="handleReactivate"
            @request-delete="deleteDebt"
          />

          <Transition name="expand">
            <div v-if="expandedDebt === debt.id" class="debt-expanded">
              <div class="payment-calendar">
                <div class="calendar-header-bar">
                  <h4 class="calendar-title">Calendario de Pagos</h4>
                  <span class="calendar-year">{{ currentYear }}</span>
                </div>
                <DebtCalendar
                  :debt="debt"
                  :payment-history="paymentHistory"
                  :loading="loadingHistory"
                  @month-click="handleMonthClick(debt, $event)"
                />
              </div>
            </div>
          </Transition>
        </div>

        <div v-if="!debts.length" class="empty-state">
          <p class="empty-text">No hay deudas registradas</p>
          <button class="btn btn-primary" @click="showNewDebtModal = true">
            Crear primera deuda
          </button>
        </div>
      </div>
    </template>

    <NewDebtModal
      :show="showNewDebtModal"
      @close="showNewDebtModal = false"
      @created="onDebtCreated"
    />

    <EditDebtModal
      :show="showEditModal"
      :debt="editDebtData"
      @close="showEditModal = false"
      @updated="onDebtUpdated"
    />

    <PaymentModal
      :show="showPaymentModal"
      :debt="paymentDebt"
      @close="showPaymentModal = false"
      @paid="onPaymentRecorded"
    />

    <AmortizationModal
      :show="showAmortModal"
      :debt-id="amortDebtId"
      @close="showAmortModal = false"
    />

    <ConfirmDialog
      v-model="confirmState.show"
      :title="confirmState.title"
      :message="confirmState.message"
      :type="confirmState.type"
      :confirm-text="confirmState.confirmText"
      :cancel-text="confirmState.cancelText"
      :loading="confirmState.loading"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useConfirm } from '@/composables/useConfirm'
import DebtSummary from '@/components/debts/DebtSummary.vue'
import DebtRow from '@/components/debts/DebtRow.vue'
import DebtCalendar from '@/components/debts/DebtCalendar.vue'
import NewDebtModal from '@/components/debts/NewDebtModal.vue'
import EditDebtModal from '@/components/debts/EditDebtModal.vue'
import PaymentModal from '@/components/debts/PaymentModal.vue'
import AmortizationModal from '@/components/debts/AmortizationModal.vue'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()
const { confirmState, confirm, handleConfirm, handleCancel } = useConfirm()

const debts = ref([])
const dueAlerts = ref([])
const loading = ref(true)
const error = ref('')

const showNewDebtModal = ref(false)
const showEditModal = ref(false)
const editDebtData = ref(null)

const showPaymentModal = ref(false)
const paymentDebt = ref(null)

const showAmortModal = ref(false)
const amortDebtId = ref('')

const expandedDebt = ref(null)
const paymentHistory = ref([])
const loadingHistory = ref(false)
const markingPaid = ref(false)

const currentYear = new Date().getFullYear()
const monthFullNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const totalDebt = computed(() => debts.value.reduce((sum, d) => sum + (d.current_balance || 0), 0))
const totalMonthlyPayment = computed(() => debts.value.reduce((sum, d) => sum + (d.minimum_payment || 0), 0))
const activeDebts = computed(() => debts.value.filter(d => d.status === 'active' && d.current_balance > 0))

const nextDueDay = computed(() => {
  const today = new Date()
  const active = activeDebts.value.filter(d => d.due_day).sort((a, b) => a.due_day - b.due_day)
  for (const d of active) {
    if (d.due_day >= today.getDate()) return `Dia ${d.due_day}`
  }
  return active.length ? `Dia ${active[0].due_day}` : '-'
})

async function toggleDebt(debtId) {
  if (expandedDebt.value === debtId) {
    expandedDebt.value = null
    paymentHistory.value = []
  } else {
    expandedDebt.value = debtId
    await loadPaymentHistory(debtId)
  }
}

async function loadPaymentHistory(debtId) {
  loadingHistory.value = true
  try {
    const { data } = await api.get(`/debts/${debtId}/payment-history`)
    paymentHistory.value = data
  } catch (e) {
    console.error('Error loading payment history:', e)
    paymentHistory.value = []
  } finally {
    loadingHistory.value = false
  }
}

async function handleMonthClick(debt, monthData) {
  const confirmed = await confirm({
    title: 'Marcar como pagado',
    message: `Marcar ${monthFullNames[monthData.month - 1]} ${monthData.year} como pagado? Se reducira el saldo en $${fmt(debt.minimum_payment)}.`,
    type: 'info',
    confirmText: 'Marcar pagado',
  })
  if (!confirmed) return

  markingPaid.value = true
  try {
    await api.post(`/debts/${debt.id}/mark-paid`, {
      year: monthData.year,
      month: monthData.month,
    })
    const idx = debts.value.findIndex((d) => d.id === debt.id)
    if (idx !== -1) {
      debts.value[idx] = {
        ...debts.value[idx],
        current_balance: Math.max(0, debts.value[idx].current_balance - debt.minimum_payment),
      }
    }
    await loadPaymentHistory(debt.id)
    await loadAlerts()
  } catch (e) {
    console.error('Error marking month as paid:', e)
  } finally {
    markingPaid.value = false
  }
}

function openEdit(debt) {
  editDebtData.value = debt
  showEditModal.value = true
}

function openPayment(debt) {
  paymentDebt.value = debt
  showPaymentModal.value = true
}

function openAmortization(debtId) {
  amortDebtId.value = debtId
  showAmortModal.value = true
}

async function handleToggleStatus(debt) {
  const isActivating = debt.status !== 'active'
  const action = isActivating ? 'activar' : 'pausar'
  const confirmed = await confirm({
    title: `${isActivating ? 'Activar' : 'Pausar'} deuda`,
    message: `Desea ${action} la deuda "${debt.name}"?${isActivating ? '' : ' No aparecera en alertas ni calendario.'}`,
    type: isActivating ? 'info' : 'warning',
    confirmText: isActivating ? 'Activar' : 'Pausar',
  })
  if (!confirmed) return
  try {
    const { data } = await api.post(`/debts/${debt.id}/toggle`)
    const idx = debts.value.findIndex((d) => d.id === debt.id)
    if (idx !== -1) debts.value[idx] = data
    await loadAlerts()
  } catch (e) {
    console.error('Error toggling debt:', e)
  }
}

async function handleReactivate(debt) {
  const confirmed = await confirm({
    title: 'Reactivar deuda',
    message: `Desea reactivar la deuda "${debt.name}"? El saldo se reiniciara al monto original.`,
    type: 'info',
    confirmText: 'Reactivar',
  })
  if (!confirmed) return
  try {
    const { data } = await api.put(`/debts/${debt.id}`, { status: 'active' })
    const idx = debts.value.findIndex((d) => d.id === debt.id)
    if (idx !== -1) debts.value[idx] = data
    await loadAlerts()
  } catch (e) {
    console.error('Error reactivating debt:', e)
  }
}

async function deleteDebt(debt) {
  const confirmed = await confirm({
    title: 'Eliminar deuda',
    message: 'Estas seguro de que deseas eliminar esta deuda? Esta accion no se puede deshacer.',
    type: 'danger',
    confirmText: 'Eliminar',
  })
  if (!confirmed) return
  try {
    await api.delete(`/debts/${debt.id}`)
    debts.value = debts.value.filter((d) => d.id !== debt.id)
    if (expandedDebt.value === debt.id) {
      expandedDebt.value = null
      paymentHistory.value = []
    }
  } catch (e) {
    console.error(e)
  }
}

async function onDebtCreated() {
  showNewDebtModal.value = false
  await loadDebts()
}

async function onDebtUpdated() {
  showEditModal.value = false
  await loadDebts()
}

async function onPaymentRecorded() {
  showPaymentModal.value = false
  await loadDebts()
  if (expandedDebt.value) {
    await loadPaymentHistory(expandedDebt.value)
  }
}

async function loadAlerts() {
  try {
    const { data } = await api.get('/debts/due-alerts')
    dueAlerts.value = data
  } catch (e) {
    console.error('Error loading alerts:', e)
  }
}

async function loadDebts() {
  loading.value = true
  error.value = ''
  try {
    const [debtsRes, alertsRes] = await Promise.all([
      api.get('/debts'),
      api.get('/debts/due-alerts'),
    ])
    debts.value = debtsRes.data
    dueAlerts.value = alertsRes.data
  } catch (e) {
    error.value = 'Error al cargar las deudas'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadDebts)
</script>

<style scoped>
.debts-page { max-width: 960px; margin: 0 auto; padding: var(--spacing-lg); }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); margin: 0; }
.btn-add { padding: var(--spacing-sm) var(--spacing-lg); font-size: 0.85rem; }

.debts-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.debt-item {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all 0.15s ease;
}
.debt-item:hover { border-color: var(--color-neutral-300); }
.debt-item.expanded {
  border-color: var(--color-primary-300);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.debt-expanded {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
  border-top: 1px solid var(--color-neutral-100);
}

.payment-calendar {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}
.calendar-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-neutral-100);
}
.calendar-title { font-size: 0.85rem; font-weight: 600; color: var(--color-neutral-900); margin: 0; }
.calendar-year { font-size: 0.75rem; color: var(--color-neutral-500); }

.alerts-section { margin-bottom: var(--spacing-md); }
.alerts-list { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.alert-card {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: 0.8rem;
}
.alert-icon { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.7rem; flex-shrink: 0; }
.alert-critical { background: var(--color-error-50); color: var(--color-error-700); }
.alert-critical .alert-icon { background: var(--color-error-100); color: var(--color-error-600); }
.alert-warning { background: var(--color-warning-50); color: var(--color-warning-700); }
.alert-warning .alert-icon { background: var(--color-warning-100); color: var(--color-warning-600); }
.alert-info { background: var(--color-primary-50); color: var(--color-primary-700); }
.alert-info .alert-icon { background: var(--color-primary-100); color: var(--color-primary-600); }

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
}
.empty-text {
  color: var(--color-neutral-400);
  font-size: 0.875rem;
  margin-bottom: var(--spacing-md);
}
.loading-state { display: flex; flex-direction: column; gap: var(--spacing-md); }
.error-state { display: flex; flex-direction: column; align-items: center; gap: var(--spacing-md); padding: var(--spacing-2xl); color: var(--color-error-500); font-size: 0.875rem; }

.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; transition: background var(--transition-fast); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }

.expand-enter-active, .expand-leave-active { transition: all 0.2s ease; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; }

@media (max-width: 768px) {
  .debts-page { padding: var(--spacing-md); }
  .debt-expanded { padding: 0 var(--spacing-md) var(--spacing-md); }
  .debt-actions-row { flex-wrap: wrap; }
}

@media (max-width: 480px) {
  .debts-page { padding: var(--spacing-sm); }
  .page-header { flex-direction: column; gap: var(--spacing-sm); align-items: stretch; }
  .btn-add { text-align: center; }
}
</style>
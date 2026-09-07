<template>
  <div class="resumen-page">
    <div class="resumen-header">
      <div>
        <h1 class="resumen-greeting">{{ greeting }}</h1>
        <p class="resumen-date">{{ todayLabel }}</p>
      </div>
    </div>

    <div v-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-sm btn-click" @click="loadAll">Reintentar</button>
    </div>

    <template v-else-if="!loading">
      <div v-if="d.financial_alert && !alertDismissed" class="resumen-alert" :class="'alert-' + d.financial_alert.type">
        <div class="alert-content">
          <div class="alert-header">
            <AlertTriangle :size="14" />
            <span>{{ d.financial_alert.message }}</span>
            <button class="alert-close" @click="alertDismissed = true" aria-label="Cerrar">
              <X :size="12" />
            </button>
          </div>
          <div v-if="d.financial_alert.options?.length" class="alert-actions">
            <button v-for="opt in d.financial_alert.options" :key="opt" class="alert-action-btn" @click="handleAlertOption(opt)">
              {{ opt }}
            </button>
          </div>
        </div>
      </div>

      <div class="available-card">
        <div class="available-top">
          <span class="available-label">Disponible</span>
        </div>
        <span class="available-value">${{ fmt(availability?.projected_available ?? d.total_balance ?? 0) }}</span>
        <div class="available-meta">
          <span>Cuentas: ${{ fmt(availability?.available ?? d.total_balance ?? 0) }}</span>
          <span>Pagos: ${{ fmt(availability?.upcoming_payments ?? totalMonthlyPayment) }}</span>
        </div>
      </div>

      <div class="resumen-grid">
        <div class="resumen-main">
          <div class="card card-section">
            <h3 class="card-title">
              <span class="title-icon">📅</span> Hoy
            </h3>
            <div v-if="todayEvents.length === 0" class="empty-msg">Nada que pagar</div>
            <div v-else class="event-list">
              <div v-for="ev in todayEvents" :key="ev.id" class="event-item" :class="eventColor(ev)" @click="goEvent(ev)">
                <span class="ev-item-title">{{ ev.title }}</span>
                <span class="ev-item-amount">{{ fmtFull(ev.amount) }}</span>
                <span class="ev-item-meta">{{ ev.type === 'income' ? 'Ingreso' : 'Pago' }}</span>
              </div>
            </div>
          </div>

          <div class="card card-section">
            <h3 class="card-title">
              <span class="title-icon">🔔</span> Próximamente
            </h3>
            <div v-if="upcomingEvents.length === 0" class="empty-msg">No hay pagos próximos</div>
            <div v-else class="event-list">
              <div v-for="ev in upcomingEvents" :key="ev.id" class="event-item" :class="eventColor(ev)" @click="goEvent(ev)">
                <span class="ev-item-title">{{ ev.title }}</span>
                <span class="ev-item-amount">{{ fmtFull(ev.amount) }}</span>
                <span class="ev-item-meta">vence en {{ daysUntil(ev.due_date) }} días</span>
              </div>
            </div>
          </div>

          <div class="card card-section">
            <h3 class="card-title">
              <span class="title-icon">📊</span> Este mes
            </h3>
            <div class="month-grid">
              <div class="month-row">
                <span>Ingresos</span>
                <strong class="income">${{ fmt(monthSummary?.expected_income ?? d.monthly_income ?? 0) }}</strong>
              </div>
              <div class="month-row">
                <span>Gastos</span>
                <strong class="expense">${{ fmt(monthSummary?.expected_expenses ?? d.monthly_expenses ?? 0) }}</strong>
              </div>
              <div class="month-divider"></div>
              <div class="month-row">
                <span>Nos queda</span>
                <strong :class="netMonthly >= 0 ? 'income' : 'expense'">${{ fmt(netMonthly) }}</strong>
              </div>
            </div>
          </div>

          <div v-if="topCategories.length" class="card card-section">
            <h3 class="card-title">
              <span class="title-icon">💸</span> ¿En qué se fue el dinero?
            </h3>
            <div class="cat-bars">
              <div v-for="cat in topCategories.slice(0, showFullCat ? topCategories.length : 4)" :key="cat.name" class="cat-row">
                <div class="cat-info">
                  <span class="cat-emoji">{{ cat.icon }}</span>
                  <span class="cat-name">{{ cat.name }}</span>
                </div>
                <div class="cat-track">
                  <div class="cat-fill" :style="{ width: cat.pct + '%', background: cat.color }" />
                </div>
                <span class="cat-amount">${{ fmt(cat.amount) }}</span>
              </div>
              <button v-if="topCategories.length > 4" class="btn-expand" @click="showFullCat = !showFullCat">
                {{ showFullCat ? 'Ver menos' : `Ver todas (${topCategories.length})` }}
              </button>
            </div>
          </div>

          <div class="card card-section">
            <h3 class="card-title">
              <span class="title-icon">📋</span> Últimos movimientos
            </h3>
            <div v-if="d.recent_transactions?.length" class="tx-list">
              <div v-for="tx in d.recent_transactions.slice(0, 5)" :key="tx.id" class="tx-item">
                <div class="tx-info">
                  <span class="tx-desc">{{ tx.description || 'Sin detalle' }}</span>
                  <span class="tx-date">{{ tx.date }}</span>
                </div>
                <span class="tx-amount" :class="tx.type">
                  {{ tx.type === 'income' ? '+' : '-' }}${{ fmt(tx.amount) }}
                </span>
              </div>
            </div>
            <div v-else class="empty-msg">Registra tu primer movimiento con el botón +</div>
          </div>
        </div>

        <div class="resumen-sidebar">
          <div class="card card-tinted card-deudas">
            <h3 class="card-title">Lo que debemos</h3>
            <div class="side-rows">
              <div class="side-row">
                <span class="side-label">Total</span>
                <span class="side-value expense">${{ fmt(d.total_debt) }}</span>
              </div>
              <div class="side-row">
                <span class="side-label">Pagamos al mes</span>
                <span class="side-value">${{ fmt(totalMonthlyPayment) }}</span>
              </div>
              <div class="side-row">
                <span class="side-label">Ya pagamos</span>
                <span class="side-value">{{ paidCount }}/{{ totalDebts }}</span>
              </div>
            </div>
            <router-link to="/debts" class="card-link">Ver mis deudas</router-link>
          </div>

          <div v-if="d.savings_summary?.goals?.length" class="card card-tinted card-metas">
            <h3 class="card-title">Nuestras metas</h3>
            <div class="side-list">
              <div v-for="g in d.savings_summary.goals.slice(0, 3)" :key="g.name" class="side-list-item">
                <div class="side-list-info">
                  <span class="side-list-name">{{ g.name }}</span>
                  <div class="side-mini-bar">
                    <div class="side-mini-fill" :style="{ width: Math.min((g.current / g.target) * 100, 100) + '%' }" />
                  </div>
                </div>
                <span class="side-list-value">{{ Math.round((g.current / g.target) * 100) }}%</span>
              </div>
            </div>
            <router-link to="/goals" class="card-link">Ver metas</router-link>
          </div>

          <div v-if="d.budget_status?.length" class="card card-tinted card-presupuesto">
            <h3 class="card-title">Cómo vamos con el presupuesto</h3>
            <div class="budget-list">
              <div v-for="b in d.budget_status.slice(0, 3)" :key="b.category" class="budget-item">
                <div class="budget-header">
                  <span class="budget-name">{{ b.category }}</span>
                  <span class="budget-badge" :class="'badge-' + b.status">
                    {{ b.status === 'ok' ? '✅' : b.status === 'warning' ? '⚠️' : '🚫' }}
                  </span>
                </div>
                <div class="budget-bar">
                  <div class="budget-fill" :class="'fill-' + b.status"
                    :style="{ width: Math.min((b.spent / b.budgeted) * 100, 100) + '%' }" />
                </div>
                <span class="budget-detail">${{ fmt(b.spent) }} / ${{ fmt(b.budgeted) }}</span>
              </div>
            </div>
          </div>

          <div class="card card-tinted card-coach">
            <h3 class="card-title">
              <span class="title-icon">🧠</span> Family Coach
            </h3>
            <div v-if="suggestions.length === 0" class="empty-msg">No hay sugerencias ahora</div>
            <div v-else class="coach-list">
              <div v-for="s in suggestions" :key="s.name" class="coach-item">
                <p class="coach-text">{{ coachMessage(s) }}</p>
                <button class="coach-btn" @click="acceptSuggestion(s)">Agregar al calendario</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-if="loading" class="loading-state">
      <div class="resumen-grid">
        <div class="resumen-main">
          <div class="card"><SkeletonLoader variant="text" width="100%" height="80px" /></div>
          <div class="card"><SkeletonLoader variant="text" width="100%" height="120px" /></div>
          <div class="card"><SkeletonLoader variant="text" width="100%" height="100px" /></div>
        </div>
        <div class="resumen-sidebar">
          <div class="card"><SkeletonLoader variant="text" width="100%" height="80px" /></div>
          <div class="card"><SkeletonLoader variant="text" width="100%" height="60px" /></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, X } from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { useCurrency } from '@/composables/useCurrency'
import { useDashboard } from '@/composables/useDashboard'
import { useCalendarStore } from '@/stores/useCalendar'
import { useNotifications } from '@/composables/useNotifications'
import { eventsService } from '@/services/events'

const router = useRouter()
const { fmt, fmtFull } = useCurrency()
const store = useCalendarStore()
const { suggestions, loadSuggestions, acceptSuggestion } = useNotifications()

const {
  loading: dashLoading, error: dashError, d,
  topCategories, upcomingPayments, monthlyPayments,
  totalMonthlyPaid, totalMonthlyPayment, totalDebts, paidCount,
  loadData,
} = useDashboard()

const loading = computed(() => dashLoading.value)
const error = computed(() => dashError.value)

const alertDismissed = ref(false)
const showFullCat = ref(false)

const availability = ref(null)
const monthSummary = ref(null)
const todayEvents = ref([])
const upcomingEvents = ref([])

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días'
  if (h < 19) return 'Buenas tardes'
  return 'Buenas noches'
})

const todayLabel = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' })
})

const netMonthly = computed(() => {
  const income = monthSummary.value?.expected_income ?? d.value.monthly_income ?? 0
  const expenses = monthSummary.value?.expected_expenses ?? d.value.monthly_expenses ?? 0
  return income - expenses
})

function daysUntil(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return Math.round((d - now) / 86400000)
}

function eventColor(ev) {
  if (ev.status === 'paid') return 'ev-green'
  if (ev.type === 'income') return 'ev-blue'
  if (ev.type === 'goal') return 'ev-purple'
  const diff = daysUntil(ev.due_date)
  if (diff < 0) return 'ev-red'
  if (ev.cutoff_date && daysUntil(ev.cutoff_date) <= 1) return 'ev-red'
  if (diff <= (ev.reminder_days_before || 3)) return 'ev-yellow'
  return 'ev-green'
}

function coachMessage(s) {
  return `Tu pago de ${s.name.toLowerCase()} suele hacerse alrededor del día ${s.anchor_day}. ¿Quieres agregarlo como recurrente?`
}

function goEvent(ev) {
  router.push({ path: '/calendar', query: { event_id: ev.id } })
}

function handleAlertOption(option) {
  const opt = option.toLowerCase()
  if (opt.includes('pago extra') || opt.includes('pago')) router.push('/calendar')
  else if (opt.includes('deuda') || opt.includes('reduci')) router.push('/debts')
  else if (opt.includes('gasto') || opt.includes('presupuesto')) router.push('/config')
  else if (opt.includes('ingreso') || opt.includes('ingres')) router.push('/config')
}

async function loadEvents() {
  try {
    const [availRes, upcomingRes] = await Promise.all([
      eventsService.availability(30),
      eventsService.upcoming(30),
    ])
    availability.value = availRes.data
    monthSummary.value = availRes.data

    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayStr = today.toISOString().slice(0, 10)

    const all = upcomingRes.data || []
    todayEvents.value = all.filter(e => e.due_date === todayStr && e.status !== 'paid').slice(0, 5)
    upcomingEvents.value = all.filter(e => e.due_date > todayStr && e.status !== 'paid').slice(0, 5)
  } catch {
    availability.value = null
    todayEvents.value = []
    upcomingEvents.value = []
  }
}

async function loadAll() {
  await Promise.all([loadData(), loadEvents(), loadSuggestions()])
}

onMounted(loadAll)
</script>

<style scoped>
.resumen-page { max-width: 1100px; margin: 0 auto; padding: 0 var(--spacing-md); }

.resumen-header { margin-bottom: var(--spacing-md); }
.resumen-greeting { font-family: var(--font-display); font-size: 1.4rem; font-weight: 700; margin: 0; color: var(--color-neutral-900); }
.resumen-date { color: var(--color-neutral-500); font-size: 0.85rem; margin: 4px 0 0; }

.resumen-alert {
  display: flex; align-items: center; gap: 6px; padding: 8px 12px;
  border-radius: var(--radius-md); font-size: 0.75rem; font-weight: 500;
  margin-bottom: var(--spacing-md); animation: fadeIn 200ms ease;
}
.resumen-alert.alert-critical { background: var(--color-error-50); color: var(--color-error-600); }
.resumen-alert.alert-warning { background: var(--color-warning-50); color: var(--color-warning-600); }
.resumen-alert.alert-info { background: var(--color-info-50); color: var(--color-info-600); }
.alert-content { display: flex; flex-direction: column; gap: 6px; }
.alert-header { display: flex; align-items: center; gap: 6px; }
.alert-close { background: none; border: none; cursor: pointer; padding: 2px; margin-left: auto; color: inherit; opacity: 0.6; }
.alert-close:hover { opacity: 1; }
.alert-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.alert-action-btn {
  padding: 3px 8px; border-radius: var(--radius-sm); font-size: 0.7rem; font-weight: 500;
  border: 1px solid currentColor; background: transparent; cursor: pointer;
}
.alert-action-btn:hover { background: rgba(0,0,0,0.05); }

.available-card {
  background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff;
  border-radius: 20px; padding: 20px; margin-bottom: var(--spacing-md);
}
.available-top { display: flex; justify-content: space-between; align-items: center; }
.available-label { font-size: 0.8rem; opacity: 0.85; }
.available-link { font-size: 0.75rem; color: #fff; opacity: 0.8; text-decoration: none; }
.available-link:hover { opacity: 1; text-decoration: underline; }
.available-value { font-size: 2rem; font-weight: 800; font-family: var(--font-mono); display: block; margin: 4px 0; }
.available-meta { display: flex; gap: 12px; font-size: 0.75rem; opacity: 0.8; }

.resumen-grid { display: grid; grid-template-columns: 1fr 300px; gap: var(--spacing-md); align-items: start; }
.resumen-main { display: flex; flex-direction: column; gap: var(--spacing-md); }
.resumen-sidebar { display: flex; flex-direction: column; gap: var(--spacing-md); position: sticky; top: var(--spacing-md); }

.card {
  background: var(--color-neutral-0); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-neutral-100);
}
.card-tinted { border-radius: var(--radius-lg); padding: var(--spacing-lg); }
.card-deudas { background: var(--color-surface-tinted-yellow); border: 1px solid var(--color-warning-100); }
.card-metas { background: var(--color-surface-tinted-blue); border: 1px solid var(--color-primary-100); }
.card-presupuesto { background: var(--color-surface-tinted-yellow); border: 1px solid var(--color-warning-100); }
.card-coach { background: var(--color-neutral-0); border: 1px solid var(--color-neutral-100); }

.card-title {
  font-family: var(--font-display); font-size: 0.9rem; font-weight: 600;
  color: var(--color-neutral-900); margin-bottom: var(--spacing-md);
}
.card-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-md); }
.card-title-row .card-title { margin-bottom: 0; }
.title-icon { margin-right: 4px; }

.empty-msg { color: var(--color-neutral-500); font-size: 0.85rem; text-align: center; padding: var(--spacing-md) 0; }

.event-list { display: flex; flex-direction: column; gap: 8px; }
.event-item {
  display: flex; align-items: center; gap: 8px; padding: 10px 12px;
  border-radius: 12px; cursor: pointer; transition: background 150ms;
}
.event-item:hover { filter: brightness(0.97); }
.ev-item-title { font-size: 0.85rem; font-weight: 600; flex: 1; }
.ev-item-amount { font-size: 0.85rem; font-weight: 700; font-family: var(--font-mono); }
.ev-item-meta { font-size: 0.7rem; color: var(--color-neutral-500); white-space: nowrap; }
.ev-green { background: var(--color-success-50); }
.ev-yellow { background: var(--color-warning-50); }
.ev-red { background: var(--color-error-50); }
.ev-blue { background: var(--color-info-50); }
.ev-purple { background: #f3e8ff; }

.month-grid { display: flex; flex-direction: column; gap: 10px; }
.month-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
.month-divider { height: 1px; background: var(--color-neutral-100); margin: 4px 0; }
.income { color: var(--color-success-700); }
.expense { color: var(--color-error-700); }

.cat-bars { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.cat-row { display: grid; grid-template-columns: 140px 1fr 80px; align-items: center; gap: var(--spacing-sm); }
.cat-info { display: flex; align-items: center; gap: var(--spacing-xs); min-width: 0; }
.cat-emoji { font-size: 1rem; }
.cat-name { font-size: 0.8rem; font-weight: 500; color: var(--color-neutral-700); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cat-track { height: 8px; background: var(--color-neutral-100); border-radius: 4px; overflow: hidden; }
.cat-fill { height: 100%; border-radius: 4px; transition: width 500ms ease; }
.cat-amount { font-size: 0.8rem; font-weight: 600; font-family: var(--font-mono); text-align: right; }

.tx-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.tx-item { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-100); }
.tx-item:last-child { border-bottom: none; }
.tx-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.tx-desc { font-size: 0.85rem; font-weight: 500; color: var(--color-neutral-800); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tx-date { font-size: 0.7rem; color: var(--color-neutral-400); }
.tx-amount { font-size: 0.85rem; font-weight: 600; font-family: var(--font-mono); }
.tx-amount.income { color: var(--color-success-600); }
.tx-amount.expense { color: var(--color-error-600); }

.side-rows { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.side-row { display: flex; justify-content: space-between; align-items: center; }
.side-label { font-size: 0.8rem; color: var(--color-neutral-500); }
.side-value { font-size: 0.9rem; font-weight: 600; font-family: var(--font-mono); color: var(--color-neutral-900); }
.side-value.income { color: var(--color-success-600); }
.side-value.expense { color: var(--color-error-600); }

.side-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.side-list-item { display: flex; justify-content: space-between; align-items: center; }
.side-list-info { display: flex; flex-direction: column; gap: 4px; min-width: 0; flex: 1; }
.side-list-name { font-size: 0.8rem; font-weight: 500; color: var(--color-neutral-700); }
.side-list-value { font-size: 0.75rem; font-weight: 600; color: var(--color-primary-600); }
.side-mini-bar { width: 100%; height: 4px; background: var(--color-neutral-200); border-radius: 2px; overflow: hidden; }
.side-mini-fill { height: 100%; background: var(--color-primary-500); border-radius: 2px; transition: width 300ms ease; }

.budget-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.budget-item { padding: var(--spacing-sm); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-md); }
.budget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.budget-name { font-size: 0.8rem; font-weight: 500; color: var(--color-neutral-700); }
.budget-badge { font-size: 0.75rem; }
.budget-bar { height: 6px; background: var(--color-neutral-100); border-radius: 3px; overflow: hidden; margin-bottom: 4px; }
.budget-fill { height: 100%; border-radius: 3px; transition: width 300ms ease; }
.fill-ok { background: var(--color-success-500); }
.fill-warning { background: var(--color-warning-500); }
.fill-over { background: var(--color-error-500); }
.budget-detail { font-size: 0.7rem; color: var(--color-neutral-500); }

.coach-list { display: flex; flex-direction: column; gap: 10px; }
.coach-item { background: var(--color-neutral-50); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.coach-text { font-size: 0.82rem; color: var(--color-neutral-700); margin: 0; }
.coach-btn {
  align-self: flex-start; border: none; background: var(--color-primary-600); color: #fff;
  padding: 8px 14px; border-radius: 10px; font-size: 0.8rem; font-weight: 600; cursor: pointer;
}
.coach-btn:hover { background: var(--color-primary-700); }

.card-link {
  display: inline-block; margin-top: var(--spacing-md); font-size: 0.8rem;
  color: var(--color-primary-600); text-decoration: none; font-weight: 500;
}
.card-link:hover { text-decoration: underline; }

.btn-expand {
  background: none; border: none; color: var(--color-primary-600); font-size: 0.8rem;
  font-weight: 500; cursor: pointer; padding: var(--spacing-xs) 0; text-decoration: none;
}
.btn-expand:hover { color: var(--color-primary-700); }

.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); background: var(--color-neutral-100); color: var(--color-neutral-700); }

.error-state { display: flex; flex-direction: column; align-items: center; gap: var(--spacing-md); padding: var(--spacing-2xl); color: var(--color-error-500); }
.loading-state { padding: var(--spacing-md) 0; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .resumen-grid { grid-template-columns: 1fr; }
  .resumen-sidebar { position: static; }
}

@media (max-width: 640px) {
  .resumen-page { padding: 0 var(--spacing-sm); }
  .resumen-header { flex-direction: column; gap: 8px; }
  .cat-row { grid-template-columns: 100px 1fr 60px; font-size: 0.8rem; }
}
</style>

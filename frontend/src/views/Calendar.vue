<template>
  <div class="calendar-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">Calendario</h2>
        <p class="page-subtitle">Lo que tienes que pagar, cuánto y cuándo.</p>
      </div>
      <div class="header-actions">
        <select v-model="availabilityDays" @change="onAvailabilityDays" class="availability-select">
          <option :value="7">7 días</option>
          <option :value="30">30 días</option>
        </select>
        <button class="today-btn" @click="goToday">Hoy</button>
      </div>
    </div>

    <div v-if="store.availabilityLoading" class="availability-skeleton">
      <div v-for="n in 4" :key="n" class="skeleton-line"></div>
    </div>
    <div v-else-if="store.availabilitySummary" class="availability-panel">
      <div class="avail-card">
        <span class="avail-label">Disponible</span>
        <span class="avail-value">{{ store.availabilitySummary.available }}</span>
      </div>
      <div class="avail-card">
        <span class="avail-label">Pagos próximos</span>
        <span class="avail-value avail-warn">{{ store.availabilitySummary.upcoming }}</span>
      </div>
      <div class="avail-card">
        <span class="avail-label">Proyectado</span>
        <span class="avail-value" :class="projectedClass()">{{ store.availabilitySummary.projected }}</span>
      </div>
      <div class="avail-card">
        <span class="avail-label">Efectivo necesario</span>
        <span class="avail-value avail-warn">{{ store.availabilitySummary.cashNeeded }}</span>
      </div>
      <div class="avail-card">
        <span class="avail-label">Ingresos esperados</span>
        <span class="avail-value avail-ok">{{ store.availabilitySummary.expectedIncome }}</span>
      </div>
      <div class="avail-card">
        <span class="avail-label">Gastos esperados</span>
        <span class="avail-value avail-warn">{{ store.availabilitySummary.expectedExpenses }}</span>
      </div>
      <span class="avail-badge">[No verificado] proyección</span>
    </div>

    <div class="legend">
      <span class="legend-item"><i class="dot ev-green"></i> Al día</span>
      <span class="legend-item"><i class="dot ev-yellow"></i> Próximo</span>
      <span class="legend-item"><i class="dot ev-red"></i> Vence / atrasado</span>
      <span class="legend-item"><i class="dot ev-blue"></i> Ingreso</span>
      <span class="legend-item"><i class="dot ev-purple"></i> Meta</span>
    </div>

    <div class="cal-toolbar">
      <button class="nav-btn" @click="prevMonth" aria-label="Mes anterior"><ChevronLeft :size="20" /></button>
      <span class="cal-month">{{ monthLabel }}</span>
      <button class="nav-btn" @click="nextMonth" aria-label="Mes siguiente"><ChevronRight :size="20" /></button>
    </div>

    <div v-if="store.loading" class="cal-grid">
      <div v-for="n in 42" :key="n" class="cal-cell skeleton-cell"></div>
    </div>

    <div v-else class="cal-grid">
      <div
        v-for="(cell, i) in calendarDays"
        :key="i"
        class="cal-cell"
        :class="{ 'out-month': !cell.inMonth, 'is-today': cell.isToday }"
      >
        <span class="cell-day" :class="{ 'today-pill': cell.isToday }">{{ cell.day }}</span>
        <div class="cell-events">
          <button
            v-for="ev in cell.events"
            :key="ev.id"
            class="ev-chip"
            :class="eventColor(ev)"
            @click="openEvent(ev)"
          >
            <component :is="typeIcon(ev.type)" :size="13" class="ev-icon" />
            <span class="ev-title">{{ ev.title }}</span>
            <span class="ev-amount">{{ fmt(ev.amount) }}</span>
          </button>
        </div>
      </div>
    </div>

    <p v-if="!store.loading && store.events.length === 0" class="empty-state">
      Este mes está tranquilo. Cuando agregues un pago o una obligación, aparecerá aquí.
    </p>

    <button class="fab" @click="store.createOpen = true" aria-label="Nuevo evento">
      <Plus :size="26" />
    </button>

    <!-- Detalle del evento -->
    <div v-if="store.detailOpen" class="sheet-backdrop" @click.self="store.closeDetail">
      <div class="sheet">
        <button class="sheet-close" @click="store.closeDetail" aria-label="Cerrar"><X :size="20" /></button>
        <div v-if="selectedEvent" class="sheet-body">
          <div class="sheet-head">
            <component :is="typeIcon(selectedEvent.type)" :size="22" />
            <h3>{{ selectedEvent.title }}</h3>
          </div>
          <div class="sheet-amount">{{ fmtFull(selectedEvent.amount) }}</div>

          <div class="sheet-row">
            <Clock :size="16" /><span>Fecha límite</span>
            <strong>{{ fmtDate(selectedEvent.due_date) }}</strong>
          </div>
          <div v-if="selectedEvent.recommended_date" class="sheet-row">
            <CalendarDays :size="16" /><span>Recomendado</span>
            <strong>{{ fmtDate(selectedEvent.recommended_date) }}</strong>
          </div>
          <div class="sheet-row">
            <Check :size="16" /><span>Estado</span>
            <strong :class="statusClass(selectedEvent)">{{ statusLabel(selectedEvent) }}</strong>
          </div>
          <div v-if="selectedEvent.payment_method" class="sheet-row">
            <Wallet :size="16" /><span>Forma de pago</span>
            <strong>{{ methodLabel(selectedEvent.payment_method) }}</strong>
          </div>
          <div v-if="selectedEvent.responsibility" class="sheet-row">
            <User :size="16" /><span>Responsable</span>
            <strong>{{ selectedEvent.responsibility }}</strong>
          </div>
          <div v-if="selectedEvent.consequence_note" class="sheet-note">
            {{ selectedEvent.consequence_note }}
          </div>

          <button
            v-if="selectedEvent.status !== 'paid'"
            class="pay-btn"
            @click="onPay(selectedEvent)"
          >
            <Check :size="18" /> Marcar como pagado
          </button>
          <button v-else class="paid-flag" disabled>
            <Check :size="18" /> Ya está pagado
          </button>

          <button
            v-if="selectedEvent.obligation_id"
            class="link-btn"
            @click="showObligationInfo"
          >
            Ver obligación <ArrowRight :size="15" />
          </button>
        </div>
      </div>
    </div>

    <!-- Crear evento -->
    <div v-if="store.createOpen" class="sheet-backdrop" @click.self="store.createOpen = false">
      <div class="sheet">
        <button class="sheet-close" @click="store.createOpen = false" aria-label="Cerrar"><X :size="20" /></button>
        <h3 class="form-title">Nuevo evento</h3>
        <form class="event-form" @submit.prevent="onCreate">
          <label>Título
            <input v-model="form.title" type="text" required placeholder="Ej: Internet" />
          </label>
          <label>Tipo
            <select v-model="form.type">
              <option value="expense">Gasto</option>
              <option value="payment">Pago</option>
              <option value="debt">Deuda</option>
              <option value="income">Ingreso</option>
              <option value="goal">Meta</option>
            </select>
          </label>
          <label>Monto
            <input v-model="form.amount" type="number" min="1" required placeholder="85000" />
          </label>
          <label>Fecha límite
            <input v-model="form.due_date" type="date" required />
          </label>
          <label>Forma de pago
            <select v-model="form.payment_method">
              <option :value="null">No especificada</option>
              <option value="card">Tarjeta</option>
              <option value="cash">Efectivo</option>
              <option value="transfer">Transferencia</option>
            </select>
          </label>
          <p v-if="formError" class="form-error">{{ formError }}</p>
          <div class="form-actions">
            <button type="button" class="ghost-btn" @click="createOpen = false">Cancelar</button>
            <button type="submit" class="pay-btn">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Plus, CreditCard, TrendingUp, Target, Wallet, Bell, Check,
  ChevronLeft, ChevronRight, X, ArrowRight, CalendarDays, Clock, User,
} from 'lucide-vue-next'
import { useCalendarStore } from '@/stores/useCalendar'
import { useToast } from '@/composables/useToast'

const store = useCalendarStore()
const toast = useToast()

const WEEKDAYS = ['L', 'M', 'M', 'J', 'V', 'S', 'D']

const monthLabel = computed(() =>
  new Date(store.year.value, store.month.value - 1, 1).toLocaleDateString('es-CO', { month: 'long', year: 'numeric' })
)

const calendarDays = computed(() => {
  const now = new Date()
  const y = Number.isFinite(store.year.value) ? store.year.value : now.getFullYear()
  const m = Number.isFinite(store.month.value) ? store.month.value : now.getMonth() + 1
  const first = new Date(y, m - 1, 1)
  const offset = (first.getDay() + 6) % 7
  const start = new Date(y, m - 1, 1 - offset)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const cells = []
  for (let i = 0; i < 42; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    if (isNaN(d.getTime())) continue
    const inMonth = d.getMonth() === m - 1
    cells.push({
      day: d.getDate(),
      dateStr: d.toISOString().slice(0, 10),
      inMonth,
      isToday: d.getTime() === today.getTime(),
      events: [],
    })
  }
  for (const ev of store.events) {
    const cell = cells.find((c) => c.dateStr === ev.due_date)
    if (cell) cell.events.push(ev)
  }
  return cells
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
  if (diff <= (ev.reminder_days_before || 3)) return 'ev-yellow'
  return 'ev-green'
}

function typeIcon(type) {
  if (type === 'income') return TrendingUp
  if (type === 'goal') return Target
  if (type === 'debt') return CreditCard
  if (type === 'payment') return Wallet
  return Bell
}

function statusLabel(ev) {
  if (ev.status === 'paid') return 'Pagado'
  const diff = daysUntil(ev.due_date)
  if (diff < 0) return 'Atrasado'
  if (diff === 0) return 'Vence hoy'
  if (diff <= (ev.reminder_days_before || 3)) return 'Próximo'
  return 'Pendiente'
}

function statusClass(ev) {
  return ev.status === 'paid' ? 'st-green' : daysUntil(ev.due_date) <= 0 ? 'st-red' : 'st-yellow'
}

function methodLabel(m) {
  return { card: 'Tarjeta', cash: 'Efectivo', transfer: 'Transferencia' }[m] || m
}

const form = ref({ title: '', type: 'expense', amount: '', due_date: '', payment_method: null })
const formError = ref(null)
const availabilityDays = ref(7)

async function onAvailabilityDays() {
  await store.fetchAvailability(availabilityDays.value)
}

function projectedClass() {
  const val = store.availabilitySummary?.projected || ''
  const hasNeg = val.includes('-')
  return hasNeg ? 'avail-danger' : 'avail-ok'
}

function prevMonth() {
  let m = store.month.value - 1
  let y = store.year.value
  if (m < 1) { m = 12; y-- }
  store.fetchMonth(y, m)
}
function nextMonth() {
  let m = store.month.value + 1
  let y = store.year.value
  if (m > 12) { m = 1; y++ }
  store.fetchMonth(y, m)
}
function goToday() {
  const now = new Date()
  store.fetchMonth(now.getFullYear(), now.getMonth() + 1)
}

function openEvent(ev) { store.openEvent(ev) }
function closeDetail() { store.closeDetail() }

async function onPay(ev) {
  const res = await store.markPaid(ev)
  if (res.error) toast.error(res.error)
  else toast.success(`${ev.title} quedó pagado.`)
}

function showObligationInfo() {
  toast.info('Este pago hace parte de una obligación recurrente: se crea automáticamente cada mes.')
}

async function onCreate() {
  formError.value = null
  if (!form.value.title || !form.value.amount || !form.value.due_date) {
    formError.value = 'Completa título, monto y fecha.'
    return
  }
  const res = await store.createEvent({
    title: form.value.title,
    type: form.value.type,
    amount: parseFloat(form.value.amount),
    due_date: form.value.due_date,
    payment_method: form.value.payment_method,
  })
  if (res.error) formError.value = res.error
  else toast.success('Evento agregado al calendario.')
}

onMounted(() => {
  store.fetchMonth()
  store.fetchObligations()
  store.fetchAvailability(7)
})
</script>

<style scoped>
.calendar-page { padding: 16px; max-width: 980px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.header-actions { display: flex; align-items: center; gap: 10px; }
.availability-select {
  padding: 6px 10px; border: 1px solid var(--border, #e5e7eb); border-radius: 999px;
  background: var(--surface, #fff); font-size: 0.85rem; font-weight: 600; cursor: pointer;
}
.availability-skeleton { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
.skeleton-line { height: 56px; background: var(--skeleton, #eef0f3); border-radius: 12px; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.availability-panel {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; position: relative;
}
.avail-card {
  background: var(--surface, #fff); border: 1px solid var(--border, #eef0f3); border-radius: 14px;
  padding: 12px; display: flex; flex-direction: column; gap: 4px;
}
.avail-label { font-size: 0.75rem; color: var(--text-muted, #6b7280); }
.avail-value { font-size: 1.05rem; font-weight: 800; }
.avail-ok { color: #15803d; }
.avail-warn { color: #a16207; }
.avail-danger { color: #b91c1c; }
.avail-badge {
  position: absolute; top: -10px; right: 10px; background: var(--hover, #f3f4f6); color: var(--text-muted, #6b7280);
  font-size: 0.65rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; border: 1px solid var(--border, #e5e7eb);
}
.today-btn {
  border: 1px solid var(--border, #e5e7eb); background: var(--surface, #fff);
  border-radius: 999px; padding: 6px 14px; cursor: pointer; font-weight: 600;
}
.legend { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0; font-size: 0.78rem; color: var(--text-muted, #6b7280); }
.legend-item { display: flex; align-items: center; gap: 5px; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.cal-toolbar { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.cal-month { text-transform: capitalize; font-weight: 700; font-size: 1.05rem; min-width: 170px; }
.nav-btn { border: none; background: transparent; cursor: pointer; border-radius: 50%; padding: 6px; }
.nav-btn:hover { background: var(--hover, #f3f4f6); }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
.cal-cell {
  background: var(--surface, #fff); border: 1px solid var(--border, #eef0f3);
  border-radius: 14px; min-height: 96px; padding: 6px; display: flex; flex-direction: column; gap: 4px;
}
.out-month { background: var(--surface-2, #fafafa); opacity: 0.6; }
.is-today { border-color: var(--primary, #2563eb); }
.cell-day { font-size: 0.8rem; font-weight: 600; color: var(--text-muted, #6b7280); }
.today-pill {
  background: var(--primary, #2563eb); color: #fff; border-radius: 50%;
  width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center;
}
.cell-events { display: flex; flex-direction: column; gap: 3px; overflow: hidden; }
.ev-chip {
  display: flex; align-items: center; gap: 4px; border: none; cursor: pointer;
  border-radius: 8px; padding: 3px 6px; font-size: 0.72rem; text-align: left; color: #111;
}
.ev-icon { flex-shrink: 0; }
.ev-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ev-amount { margin-left: auto; font-weight: 700; }
.ev-green { background: #dcfce7; }
.ev-yellow { background: #fef9c3; }
.ev-red { background: #fee2e2; }
.ev-blue { background: #dbeafe; }
.ev-purple { background: #f3e8ff; }
.skeleton-cell { background: var(--skeleton, #eef0f3); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state { text-align: center; color: var(--text-muted, #6b7280); margin-top: 24px; }

.fab {
  position: fixed; right: 20px; bottom: 84px; width: 56px; height: 56px; border-radius: 50%;
  border: none; background: var(--primary, #2563eb); color: #fff; cursor: pointer;
  box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4); display: flex; align-items: center; justify-content: center;
}

.sheet-backdrop {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4);
  display: flex; align-items: flex-end; justify-content: center; z-index: 50;
}
.sheet {
  background: var(--surface, #fff); width: 100%; max-width: 460px; border-radius: 20px 20px 0 0;
  padding: 20px; position: relative; max-height: 88vh; overflow: auto;
}
.sheet-close { position: absolute; top: 14px; right: 14px; border: none; background: transparent; cursor: pointer; }
.sheet-head { display: flex; align-items: center; gap: 8px; }
.sheet-head h3 { margin: 0; }
.sheet-amount { font-size: 1.6rem; font-weight: 800; margin: 6px 0 14px; }
.sheet-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border, #f1f3f5); }
.sheet-row span { color: var(--text-muted, #6b7280); margin-right: auto; }
.sheet-note {
  background: var(--hover, #fff7ed); border-left: 3px solid #f59e0b; padding: 8px 10px;
  border-radius: 8px; margin: 10px 0; font-size: 0.82rem;
}
.pay-btn {
  width: 100%; margin-top: 14px; border: none; background: var(--primary, #2563eb); color: #fff;
  padding: 12px; border-radius: 12px; font-weight: 700; cursor: pointer; display: flex; gap: 6px; justify-content: center;
}
.paid-flag {
  width: 100%; margin-top: 14px; border: 1px solid #bbf7d0; background: #f0fdf4; color: #15803d;
  padding: 12px; border-radius: 12px; font-weight: 700; display: flex; gap: 6px; justify-content: center; cursor: default;
}
.link-btn {
  width: 100%; margin-top: 10px; border: none; background: transparent; color: var(--primary, #2563eb);
  cursor: pointer; font-weight: 600; display: flex; gap: 4px; justify-content: center; align-items: center;
}
.st-green { color: #15803d; }
.st-yellow { color: #a16207; }
.st-red { color: #b91c1c; }

.form-title { margin: 0 0 12px; }
.event-form { display: flex; flex-direction: column; gap: 12px; }
.event-form label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: 600; }
.event-form input, .event-form select {
  padding: 10px; border: 1px solid var(--border, #e5e7eb); border-radius: 10px; font-size: 0.95rem;
}
.form-error { color: #b91c1c; font-size: 0.82rem; margin: 0; }
.form-actions { display: flex; gap: 10px; }
.ghost-btn { flex: 1; border: 1px solid var(--border, #e5e7eb); background: var(--surface, #fff); border-radius: 12px; padding: 12px; font-weight: 600; cursor: pointer; }
</style>

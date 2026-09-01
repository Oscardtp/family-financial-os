<template>
  <div class="calendar-page">
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
      <div class="header-actions">
        <select v-model="availabilityDays" @change="onAvailabilityDays" class="availability-select">
          <option :value="7">7 días</option>
          <option :value="30">30 días</option>
        </select>
        <button class="today-btn" @click="goToday">Hoy</button>
      </div>
      <button class="nav-btn" @click="prevMonth" aria-label="Mes anterior"><ChevronLeft :size="20" /></button>
      <span class="cal-month">{{ monthLabel }}</span>
      <button class="nav-btn" @click="nextMonth" aria-label="Mes siguiente"><ChevronRight :size="20" /></button>
      <button class="prepare-btn" @click="openPrepare">Preparar el mes</button>
    </div>

    <div class="cal-weekdays">
      <span v-for="day in WEEKDAYS" :key="day" class="cal-weekday">{{ day }}</span>
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
        @click.self="openCreateOnDate(cell.dateStr)"
      >
        <span class="cell-day" :class="{ 'today-pill': cell.isToday }" @click.stop>{{ cell.day }}</span>
        <div class="cell-events">
          <button
            v-for="ev in cell.events"
            :key="ev.id"
            class="ev-chip"
            :class="eventColor(ev)"
            @click.stop="openEvent(ev)"
          >
            <span class="ev-title">{{ ev.title }}</span>
            <span v-if="ev.recommended_date && ev.due_date !== ev.recommended_date" class="ev-sub">{{ fmtDateShort(ev.recommended_date) }}</span>
            <span v-if="isCutoffUrgent(ev)" class="ev-cutoff-badge">🔴</span>
            <span v-if="ev.confidence < 100" class="ev-conf-badge">?</span>
            <span class="ev-amount">{{ fmt(ev.amount) }}</span>
          </button>
        </div>
      </div>
    </div>

    <p v-if="!store.loading && store.events.length === 0" class="empty-state">
      Este mes está tranquilo. Cuando agregues un pago o una obligación, aparecerá aquí.
    </p>

    <!-- Detalle del evento -->
    <div v-if="store.detailOpen" class="sheet-backdrop" @click.self="store.closeDetail">
      <div class="sheet">
        <button class="sheet-close" @click="store.closeDetail" aria-label="Cerrar"><X :size="20" /></button>
        <div v-if="store.selectedEvent" class="sheet-body">
          <div class="sheet-head">
            <component :is="typeIcon(store.selectedEvent.type)" :size="22" />
            <h3>{{ store.selectedEvent.title }}</h3>
          </div>
          <div class="sheet-amount">{{ fmtFull(store.selectedEvent.amount) }}</div>

          <div class="sheet-row">
            <Clock :size="16" /><span>Fecha límite</span>
            <strong>{{ fmtDate(store.selectedEvent.due_date) }}</strong>
          </div>
          <div v-if="store.selectedEvent.recommended_date" class="sheet-row sheet-row-ok">
            <CalendarDays :size="16" /><span>Recomendado</span>
            <strong>{{ fmtDate(store.selectedEvent.recommended_date) }}</strong>
          </div>
          <div v-if="store.selectedEvent.cutoff_date" class="sheet-row sheet-row-warn">
            <AlertTriangle :size="16" /><span>Fecha de corte</span>
            <strong>{{ fmtDate(store.selectedEvent.cutoff_date) }}</strong>
          </div>
          <div class="sheet-row">
            <Check :size="16" /><span>Estado</span>
            <strong :class="statusClass(store.selectedEvent)">{{ statusLabel(store.selectedEvent) }}</strong>
          </div>
          <div v-if="store.selectedEvent.payment_method" class="sheet-row">
            <Wallet :size="16" /><span>Forma de pago</span>
            <strong>{{ methodLabel(store.selectedEvent.payment_method) }}</strong>
          </div>
          <div v-if="store.selectedEvent.account_id" class="sheet-row">
            <PiggyBank :size="16" /><span>Cuenta</span>
            <strong>{{ accountName(store.selectedEvent.account_id) }}</strong>
          </div>
          <div v-if="store.selectedEvent.responsible_member_id" class="sheet-row">
            <User :size="16" /><span>Responsable</span>
            <strong>{{ memberName(store.selectedEvent.responsible_member_id) }}</strong>
          </div>
          <div v-if="store.selectedEvent.consequence_note" class="sheet-note">
            {{ store.selectedEvent.consequence_note }}
          </div>
          <div v-if="store.selectedEvent.confidence < 100" class="sheet-row">
            <Info :size="16" /><span>Origen</span>
            <strong>{{ confidenceLabel(store.selectedEvent) }}</strong>
          </div>

          <button
            v-if="store.selectedEvent.status !== 'paid'"
            class="pay-btn"
            @click="onPay(store.selectedEvent)"
          >
            <Check :size="18" /> Marcar como pagado
          </button>
          <button v-else class="paid-flag" disabled>
            <Check :size="18" /> Ya está pagado
          </button>

          <div class="sheet-divider"></div>

          <button
            class="edit-btn"
            @click="openEdit(store.selectedEvent)"
          >
            <Pencil :size="16" /> Editar
          </button>
          <button
            class="delete-btn"
            @click="openDelete(store.selectedEvent)"
          >
            <Trash2 :size="16" /> Eliminar
          </button>

          <button
            v-if="store.selectedEvent.obligation_id"
            class="link-btn"
            @click="showObligationInfo"
          >
            Ver obligación <ArrowRight :size="15" />
          </button>
        </div>
      </div>
    </div>

    <!-- Crear evento: picker + forms dedicados -->
    <EventTypePicker
      v-if="activeSheet === 'typePicker'"
      @select="handleTypeSelected"
      @close="closeSheet"
    />
    <ExpenseFormSheet
      v-if="activeSheet === 'expense'"
      :date="selectedDate"
      @created="onEventCreated"
      @close="closeSheet"
    />
    <IncomeFormSheet
      v-if="activeSheet === 'income'"
      :date="selectedDate"
      @created="onEventCreated"
      @close="closeSheet"
    />

    <!-- Preparar el mes -->
    <div v-if="prepareOpen" class="sheet-backdrop" @click.self="prepareOpen = false">
      <div class="sheet">
        <button class="sheet-close" @click="prepareOpen = false" aria-label="Cerrar"><X :size="20" /></button>
        <h3 class="form-title">Preparar el mes</h3>
        <div v-if="prepareLoading" class="loading-state">Cargando...</div>
        <div v-else-if="prepareData" class="prepare-grid">
          <div class="prepare-row">
            <span>Pagos programados</span>
            <strong>{{ prepareData.scheduled_payments_count }} · {{ fmtFull(prepareData.scheduled_payments_amount) }}</strong>
          </div>
          <div class="prepare-row">
            <span>Ingresos previstos</span>
            <strong class="income">{{ fmtFull(prepareData.expected_income) }}</strong>
          </div>
          <div class="prepare-row">
            <span>Deudas activas</span>
            <strong>{{ prepareData.new_debts_count }}</strong>
          </div>
          <div class="prepare-row">
            <span>Pagos recurrentes</span>
            <strong>{{ prepareData.new_recurring_count }}</strong>
          </div>
        </div>
        <div v-else class="empty-state-inline">
          <p>No pudimos cargar la preparación del mes.</p>
        </div>
        <div class="form-actions">
          <button type="button" class="ghost-btn" @click="prepareOpen = false">Cerrar</button>
          <button type="button" class="pay-btn" @click="prepareOpen = false">Listo</button>
        </div>
      </div>
    </div>

    <!-- Editar evento -->
    <EventEditSheet
      v-if="editingEvent"
      :event="editingEvent"
      @updated="onEventUpdated"
      @close="editingEvent = null"
    />

    <!-- Confirmar eliminación -->
    <ConfirmDeleteModal
      v-if="deleteTarget"
      :title="deleteTarget.title"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  CreditCard, TrendingUp, Target, Wallet, Bell, Check,
  ChevronLeft, ChevronRight, X, ArrowRight, CalendarDays, Clock, User,
  AlertTriangle, PiggyBank, Info, Pencil, Trash2,
} from 'lucide-vue-next'
import { useCalendarStore } from '@/stores/useCalendar'
import { useToast } from '@/composables/useToast'
import { useCurrency } from '@/composables/useCurrency'
import { eventsService } from '@/services/events'
import EventTypePicker from '@/components/calendar/EventTypePicker.vue'
import ExpenseFormSheet from '@/components/calendar/ExpenseFormSheet.vue'
import IncomeFormSheet from '@/components/calendar/IncomeFormSheet.vue'
import EventEditSheet from '@/components/calendar/EventEditSheet.vue'
import ConfirmDeleteModal from '@/components/calendar/ConfirmDeleteModal.vue'

const store = useCalendarStore()
const toast = useToast()
const { fmt, fmtFull, fmtDate } = useCurrency()
const router = useRouter()
const route = useRoute()

const WEEKDAYS = ['L', 'M', 'M', 'J', 'V', 'S', 'D']

const monthLabel = computed(() =>
  new Date(store.year, store.month - 1, 1).toLocaleDateString('es-CO', { month: 'long', year: 'numeric' })
)

const calendarDays = computed(() => {
  const now = new Date()
  const y = Number.isFinite(store.year) ? store.year : now.getFullYear()
  const m = Number.isFinite(store.month) ? store.month : now.getMonth() + 1
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
  if (!dateStr) return null
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
  if (diff === null) return 'ev-green'
  if (diff < 0) return 'ev-red'
  if (ev.cutoff_date && daysUntil(ev.cutoff_date) <= 1) return 'ev-red'
  if (diff <= (ev.reminder_days_before || 3)) return 'ev-yellow'
  return 'ev-green'
}

function statusLabel(ev) {
  if (ev.status === 'paid') return 'Pagado'
  const diff = daysUntil(ev.due_date)
  if (diff === null) return 'Pendiente'
  if (diff < 0) return 'Atrasado'
  if (diff === 0) return 'Vence hoy'
  if (diff <= (ev.reminder_days_before || 3)) return 'Próximo'
  return 'Pendiente'
}

function statusClass(ev) {
  if (ev.status === 'paid') return 'st-green'
  const diff = daysUntil(ev.due_date)
  if (diff === null) return 'st-yellow'
  return diff <= 0 ? 'st-red' : 'st-yellow'
}

function methodLabel(m) {
  return { card: 'Tarjeta', cash: 'Efectivo', transfer: 'Transferencia' }[m] || m
}

function typeIcon(type) {
  if (type === 'income') return TrendingUp
  if (type === 'goal') return Target
  if (type === 'debt') return CreditCard
  if (type === 'payment') return Wallet
  return Bell
}

function fmtDateShort(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const diff = Math.round((d - now) / 86400000)
  if (isNaN(diff)) return ''
  if (diff === 0) return 'hoy'
  if (diff === 1) return 'mañana'
  if (diff < 7) return `en ${diff} días`
  return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' })
}

function isCutoffUrgent(ev) {
  if (!ev.cutoff_date || ev.status === 'paid') return false
  const diff = daysUntil(ev.cutoff_date)
  if (diff === null) return false
  return diff <= 1
}

function confidenceLabel(ev) {
  if (ev.confidence >= 100) return 'Confirmado'
  if (ev.confidence >= 70) return 'Aprendido'
  return 'Estimado'
}

function accountName(id) {
  const a = store.accounts.find(x => x.id === id)
  return a ? a.name : id
}

function memberName(id) {
  const m = store.members.find(x => x.id === id)
  return m ? m.name : id
}

const activeSheet = ref(null)
const selectedDate = ref('')
const availabilityDays = ref(7)

const editingEvent = ref(null)
const deleteTarget = ref(null)
const deleteLoading = ref(false)

const prepareOpen = ref(false)
const prepareLoading = ref(false)
const prepareData = ref(null)

async function openPrepare() {
  prepareOpen.value = true
  prepareLoading.value = true
  try {
    const res = await eventsService.prepareMonth()
    prepareData.value = res.data
  } catch {
    prepareData.value = null
  } finally {
    prepareLoading.value = false
  }
}

async function onAvailabilityDays() {
  await store.fetchAvailability(availabilityDays.value)
}

function projectedClass() {
  const val = store.availabilitySummary?.projected || ''
  const hasNeg = val.includes('-')
  return hasNeg ? 'avail-danger' : 'avail-ok'
}

function prevMonth() {
  let m = store.month - 1
  let y = store.year
  if (m < 1) { m = 12; y-- }
  store.fetchRange(y, m)
}
function nextMonth() {
  let m = store.month + 1
  let y = store.year
  if (m > 12) { m = 1; y++ }
  store.fetchRange(y, m)
}
function goToday() {
  const now = new Date()
  store.fetchRange(now.getFullYear(), now.getMonth() + 1)
}

function openEvent(ev) { store.openEvent(ev) }

function openCreateOnDate(dateStr) {
  if (!dateStr) return
  selectedDate.value = dateStr
  activeSheet.value = 'typePicker'
}

function handleTypeSelected(type) {
  if (type === 'goal') {
    activeSheet.value = null
    toast.info('Para aportar a una meta, ve a la sección de Metas.')
    return
  }
  activeSheet.value = type
}

function closeSheet() {
  activeSheet.value = null
  selectedDate.value = ''
}

function onEventCreated() {
  activeSheet.value = null
  selectedDate.value = ''
  store.fetchRange()
  toast.success('Listo, ya quedó registrado.')
}

function openEdit(ev) {
  editingEvent.value = { ...ev }
  store.closeDetail()
}

async function onEventUpdated() {
  editingEvent.value = null
  store.fetchRange()
  toast.success('Listo, los cambios quedaron guardados.')
}

function openDelete(ev) {
  deleteTarget.value = ev
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleteLoading.value = true
  const res = await store.deleteEvent(deleteTarget.value.id)
  deleteLoading.value = false
  deleteTarget.value = null
  if (res.error) toast.error(res.error)
  else {
    store.fetchRange()
    toast.success('Listo, el evento se eliminó.')
  }
}

function cancelDelete() {
  deleteTarget.value = null
}

async function onPay(ev) {
  const res = await store.markPaid(ev)
  if (res.error) toast.error(res.error)
  else toast.success(`${ev.title} quedó pagado.`)
}

function showObligationInfo() {
  toast.info('Este pago hace parte de una obligación recurrente: se crea automáticamente cada mes.')
}

onMounted(async () => {
  await store.fetchRange()
  store.fetchObligations()
  store.fetchAvailability(7)
  store.fetchAccounts()
  store.fetchMembers()

  const eventId = route.query.event_id
  if (eventId) {
    const ev = store.events.find(e => e.id === eventId)
    if (ev) {
      store.openEvent(ev)
    } else {
      try {
        const res = await eventsService.get(eventId)
        store.openEvent(res.data)
      } catch {
        // ignore
      }
    }
  }
})
</script>

<style scoped>
.calendar-page { padding: 16px; max-width: 980px; margin: 0 auto; }
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
.prepare-btn {
  border: 1px solid var(--border, #e5e7eb); background: var(--surface, #fff);
  border-radius: 999px; padding: 6px 14px; cursor: pointer; font-weight: 600; font-size: 0.85rem;
}
.prepare-btn:hover { background: var(--hover, #f3f4f6); }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
.cal-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin-bottom: 6px; }
.cal-weekday {
  text-align: center; font-size: 0.75rem; font-weight: 700;
  color: var(--text-muted, #6b7280); padding: 4px 0; text-transform: uppercase;
}
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
.ev-sub { font-size: 0.65rem; color: #6b7280; white-space: nowrap; }
.ev-cutoff-badge { font-size: 0.6rem; }
.ev-conf-badge { font-size: 0.6rem; background: #e5e7eb; border-radius: 50%; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; }
.ev-amount { margin-left: auto; font-weight: 700; }
.ev-green { background: #dcfce7; }
.ev-yellow { background: #fef9c3; }
.ev-red { background: #fee2e2; }
.ev-blue { background: #dbeafe; }
.ev-purple { background: #f3e8ff; }
.skeleton-cell { background: var(--skeleton, #eef0f3); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state { text-align: center; color: var(--text-muted, #6b7280); margin-top: 24px; }

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
.sheet-row-ok { border-left: 3px solid #15803d; padding-left: 8px; }
.sheet-row-warn { border-left: 3px solid #a16207; padding-left: 8px; }
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
.sheet-divider {
  height: 1px; background: var(--border, #e5e7eb); margin: 12px 0;
}
.edit-btn {
  width: 100%; margin-top: 4px; border: none; background: transparent; color: var(--primary, #2563eb);
  padding: 10px; border-radius: 12px; font-weight: 600; cursor: pointer;
  display: flex; gap: 6px; justify-content: center; align-items: center;
  transition: background 0.15s ease;
}
.edit-btn:hover { background: #f0f5ff; }
.delete-btn {
  width: 100%; margin-top: 4px; border: none; background: transparent; color: #dc2626;
  padding: 10px; border-radius: 12px; font-weight: 600; cursor: pointer;
  display: flex; gap: 6px; justify-content: center; align-items: center;
  transition: background 0.15s ease;
}
.delete-btn:hover { background: #fef2f2; }
.st-green { color: #15803d; }
.st-yellow { color: #a16207; }
.st-red { color: #b91c1c; }

.form-title { margin: 0 0 12px; }
.event-form { display: flex; flex-direction: column; gap: 12px; }
.event-form label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: 600; }
.event-form input, .event-form select, .event-form textarea {
  padding: 10px; border: 1px solid var(--border, #e5e7eb); border-radius: 10px; font-size: 0.95rem;
}
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.form-error { color: #b91c1c; font-size: 0.82rem; margin: 0; }
.form-actions { display: flex; gap: 10px; }
.ghost-btn { flex: 1; border: 1px solid var(--border, #e5e7eb); background: var(--surface, #fff); border-radius: 12px; padding: 12px; font-weight: 600; cursor: pointer; }
.prepare-grid { display: flex; flex-direction: column; gap: 10px; }
.prepare-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; padding: 8px 0; border-bottom: 1px solid var(--border, #f1f3f5); }
.prepare-row span { color: var(--text-muted, #6b7280); }
.loading-state { text-align: center; padding: 24px; color: var(--text-muted, #6b7280); }
</style>

<template>
  <div class="calendar-page">
    <CalendarGridView
      :days="filteredCalendarDays"
      :monthLabel="monthLabel"
      :loading="store.loading"
      :selectedDate="selectedDay"
      :eventColor="eventColor"
      :fmt="fmt"
      @selectDay="selectedDay = $event"
      @createOnDate="openCreateOnDate"
      @openEvent="openEvent"
      @prev="prevMonth"
      @next="nextMonth"
      @today="goToday"
    />

    <div v-if="selectedDay" class="cal-detail-container">
      <div class="cal-detail-header">
        <span class="cal-detail-date">{{ selectedDayLabel }}</span>
        <span class="cal-detail-count">{{ selectedDayEvents.length }} movimientos</span>
      </div>
      <div v-if="selectedDayEvents.length === 0" class="cal-detail-empty">
        Elige un día con movimientos para ver el detalle.
      </div>
      <div v-else class="cal-detail-list">
        <div v-for="ev in selectedDayEvents" :key="ev.id" class="cal-detail-item" @click="openEvent(ev)">
          <div class="entry-left">
            <div class="entry-icon">
              <component :is="typeIcon(ev.type)" :size="16" />
            </div>
            <div class="entry-body">
              <div class="entry-name">{{ ev.title }}</div>
              <div v-if="ev.notes" class="entry-sub">{{ ev.notes }}</div>
            </div>
          </div>
          <span class="entry-amount" :class="eventColor(ev)">{{ fmtAmount(ev.amount) }}</span>
        </div>
      </div>
    </div>

    <CalendarEventDetailSheet
      @pay="onPay"
      @unpay="onUnpay"
      @edit="openEdit"
      @delete="openDelete"
      @showObligationInfo="onShowObligationInfo"
    />

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

    <EventEditSheet
      v-if="editingEvent"
      :event="editingEvent"
      @updated="onEventUpdated"
      @close="editingEvent = null"
    />

    <ConfirmDeleteModal
      v-if="deleteTarget"
      :title="deleteTarget.title"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />

     <ObligationDetailSheet
      v-if="obligationIdToShow"
      :show="!!obligationIdToShow"
      :obligation-id="obligationIdToShow"
      @close="obligationIdToShow = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useCurrency } from '@/composables/useCurrency'
import { eventsService, obligationsService } from '@/services/events'
import { useCalendarNavigation } from '@/composables/useCalendarNavigation'
import { useCalendarFilters } from '@/composables/useCalendarFilters'
import {
  eventColor as _eventColor,
  typeIcon as _typeIcon,
} from '@/composables/useCalendarHelpers'
import {
  TrendingUp, Target, CreditCard, Wallet, Bell,
} from 'lucide-vue-next'
import CalendarGridView from '@/components/calendar/CalendarGridView.vue'
import CalendarEventDetailSheet from '@/components/calendar/CalendarEventDetailSheet.vue'
import EventTypePicker from '@/components/calendar/EventTypePicker.vue'
import ExpenseFormSheet from '@/components/calendar/ExpenseFormSheet.vue'
import IncomeFormSheet from '@/components/calendar/IncomeFormSheet.vue'
import EventEditSheet from '@/components/calendar/EventEditSheet.vue'
import ConfirmDeleteModal from '@/components/calendar/ConfirmDeleteModal.vue'
import ObligationDetailSheet from '@/components/calendar/ObligationDetailSheet.vue'

const toast = useToast()
const { fmt } = useCurrency()
const route = useRoute()

const {
  store, monthLabel, prevMonth, nextMonth, goToday,
} = useCalendarNavigation()

const {
  filteredCalendarDays,
} = useCalendarFilters()

const todayStr = computed(() => new Date().toISOString().slice(0, 10))
const selectedDay = ref('')

function eventColor(ev) { return _eventColor(ev) }
function typeIcon(type) { return _typeIcon(type, { TrendingUp, Target, CreditCard, Wallet, Bell }) }

const selectedDayEvents = computed(() => {
  if (!selectedDay.value) return []
  return store.events.filter(ev => ev.due_date === selectedDay.value)
})

const selectedDayLabel = computed(() => {
  if (!selectedDay.value) return ''
  const d = new Date(selectedDay.value + 'T00:00:00')
  const isToday = selectedDay.value === todayStr.value
  if (isToday) return 'HOY'
  return d.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' })
})

function fmtAmount(amount) {
  const n = Number(amount)
  if (Number.isNaN(n)) return '$0'
  const abs = Math.abs(n).toLocaleString('es-CO')
  return (n < 0 ? '-$' : '$') + abs
}

const activeSheet = ref(null)
const selectedDate = ref('')
const editingEvent = ref(null)
const deleteTarget = ref(null)
const deleteLoading = ref(false)
const obligationIdToShow = ref(null)

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

console.log('[Calendar] selectedDay=', selectedDay.value, 'events=', selectedDayEvents.value.length)

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

async function onUnpay(ev) {
  const res = await store.unpayEvent(ev)
  if (res.error) toast.error(res.error)
  else toast.success('Listo, el pago se anuló.')
}

function onShowObligationInfo(obligationId) {
  obligationIdToShow.value = obligationId || null
}

onMounted(async () => {
  await store.fetchRange()
  store.fetchObligations()
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
.calendar-page { padding: var(--spacing-md); max-width: 980px; margin: 0 auto; }

.cal-detail-container {
  margin-top: var(--spacing-md); padding: var(--spacing-md);
  background: var(--color-neutral-0); border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
}
.cal-detail-header {
  display: flex; align-items: baseline; justify-content: space-between; gap: var(--spacing-sm);
  padding-bottom: var(--spacing-sm); border-bottom: 1px solid var(--color-neutral-200); margin-bottom: var(--spacing-sm);
}
.cal-detail-date {
  font-family: var(--font-display); font-size: var(--font-size-base); font-weight: 600; color: var(--color-neutral-800);
}
.cal-detail-count {
  font-size: var(--font-size-3xs); color: var(--color-neutral-500); text-transform: uppercase; letter-spacing: 0.4px;
}
.cal-detail-empty {
  color: var(--color-neutral-500); font-size: var(--font-size-sm-alt); padding: var(--spacing-sm) 0;
}
.cal-detail-list { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.cal-detail-item {
  display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md);
  background: var(--color-neutral-0); border: 1px solid var(--color-neutral-200);
  cursor: pointer; transition: background var(--transition-fast);
}
.cal-detail-item:hover { background: var(--color-neutral-50); }
.cal-detail-item .entry-left { display: flex; align-items: center; gap: var(--spacing-sm); flex: 1; min-width: 0; }
.cal-detail-item .entry-icon {
  width: 32px; height: 32px; border-radius: var(--radius-md);
  background: var(--color-neutral-100); display: inline-flex; align-items: center; justify-content: center;
  color: var(--color-neutral-600); flex-shrink: 0;
}
.cal-detail-item .entry-body { min-width: 0; }
.cal-detail-item .entry-name {
  font-size: var(--font-size-sm-alt); font-weight: 600; color: var(--color-neutral-800);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.cal-detail-item .entry-sub { font-size: var(--font-size-3xs); color: var(--color-neutral-500); margin-top: 1px; }
.cal-detail-item .entry-amount {
  font-family: var(--font-mono); font-size: var(--font-size-sm-alt); font-weight: 700;
  color: var(--color-neutral-700); white-space: nowrap; flex-shrink: 0;
}

@media (max-width: 767px) {
  .calendar-page { padding: var(--spacing-sm); }
  .cal-detail-container { padding: var(--spacing-sm); margin-top: var(--spacing-sm); }
  .cal-detail-item { padding: var(--spacing-sm); }
  .cal-detail-item .entry-icon { width: 28px; height: 28px; }
}
</style>

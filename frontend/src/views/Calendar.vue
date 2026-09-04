<template>
  <div class="calendar-page">
    <CalendarToolbar
      :viewMode="viewMode"
      :activeFilter="activeFilter"
      :monthLabel="monthLabel"
      :filters="FILTERS"
      @update:viewMode="viewMode = $event"
      @update:activeFilter="activeFilter = $event"
      @prev="prevMonth"
      @next="nextMonth"
      @today="goToday"
      @openRecurrentes="openRecurrentes"
    />

    <CalendarGridView
      v-if="viewMode === 'calendar'"
      :days="filteredCalendarDays"
      :weekdays="WEEKDAYS"
      :loading="store.loading"
      :eventColor="eventColor"
      :fmtDateShort="fmtDateShort"
      :isCutoffUrgent="isCutoffUrgent"
      :fmt="fmt"
      @createOnDate="openCreateOnDate"
      @openEvent="openEvent"
    />

    <CalendarListView
      v-else
      :groups="filteredListGrouped"
      :loading="store.loading"
      :todayStr="todayStr"
      :eventColor="eventColor"
      :fmt="fmt"
      @openEvent="openEvent"
      @createOnDate="openCreateOnDate"
    />

    <CalendarEventDetailSheet
      @pay="onPay"
      @unpay="onUnpay"
      @edit="openEdit"
      @delete="openDelete"
      @showObligationInfo="showObligationInfo"
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

    <CalendarRecurringSheet />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useCurrency } from '@/composables/useCurrency'
import { eventsService } from '@/services/events'
import { useCalendarNavigation } from '@/composables/useCalendarNavigation'
import { useCalendarFilters } from '@/composables/useCalendarFilters'
import {
  eventColor as _eventColor,
  fmtDateShort as _fmtDateShort,
  isCutoffUrgent as _isCutoffUrgent,
} from '@/composables/useCalendarHelpers'
import { useRecurringPayments } from '@/composables/useRecurringPayments'
import CalendarToolbar from '@/components/calendar/CalendarToolbar.vue'
import CalendarGridView from '@/components/calendar/CalendarGridView.vue'
import CalendarListView from '@/components/calendar/CalendarListView.vue'
import CalendarEventDetailSheet from '@/components/calendar/CalendarEventDetailSheet.vue'
import CalendarRecurringSheet from '@/components/calendar/CalendarRecurringSheet.vue'
import EventTypePicker from '@/components/calendar/EventTypePicker.vue'
import ExpenseFormSheet from '@/components/calendar/ExpenseFormSheet.vue'
import IncomeFormSheet from '@/components/calendar/IncomeFormSheet.vue'
import EventEditSheet from '@/components/calendar/EventEditSheet.vue'
import ConfirmDeleteModal from '@/components/calendar/ConfirmDeleteModal.vue'

const toast = useToast()
const { fmt } = useCurrency()
const route = useRoute()

const {
  store, monthLabel, prevMonth, nextMonth, goToday,
} = useCalendarNavigation()

const {
  WEEKDAYS, FILTERS, activeFilter, filteredCalendarDays, filteredListGrouped,
} = useCalendarFilters()

const { openRecurrentes } = useRecurringPayments()

const viewMode = ref('calendar')
const todayStr = computed(() => new Date().toISOString().slice(0, 10))

function eventColor(ev) { return _eventColor(ev) }
function fmtDateShort(d) { return _fmtDateShort(d) }
function isCutoffUrgent(ev) { return _isCutoffUrgent(ev) }

const activeSheet = ref(null)
const selectedDate = ref('')
const editingEvent = ref(null)
const deleteTarget = ref(null)
const deleteLoading = ref(false)

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

async function onUnpay(ev) {
  const res = await store.unpayEvent(ev)
  if (res.error) toast.error(res.error)
  else toast.success('Listo, el pago se anuló.')
}

function showObligationInfo() {
  toast.info('Este pago hace parte de una obligación recurrente: se crea automáticamente cada mes.')
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
</style>

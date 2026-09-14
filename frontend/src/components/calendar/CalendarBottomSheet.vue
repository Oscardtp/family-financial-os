<template>
  <div v-if="open" class="cal-sheet-backdrop" @click.self="$emit('close')">
    <div class="cal-sheet">
      <div class="cal-sheet-handle" />

      <CalendarGridView
        v-if="storeReady"
        :days="filteredCalendarDays"
        :month-label="monthLabel"
        :loading="store.loading"
        :selected-date="selectedDate"
        :filter="activeFilter"
        :event-color="eventColorFn"
        @update:filter="activeFilter = $event"
        @select-day="handleSelectDay"
        @create-on-date="handleCreateOnDate"
        @prev="prevMonth"
        @next="nextMonth"
        @today="goToday"
      />

      <div v-if="selectedEvents.length" class="cal-day-detail">
        <div class="cal-day-detail-date">
          {{ selectedDateLabel }}
        </div>
        <div class="cal-day-detail-list">
          <div
            v-for="ev in selectedEvents"
            :key="ev.id"
            class="cal-day-detail-item"
            :class="{ 'cal-day-detail-item--active': ev.id === selectedEventDetail?.id }"
            @click="handleSelectEvent(ev)"
          >
            <div class="cal-day-detail-icon">
              <component :is="typeIcon(ev.type)" :size="16" />
            </div>
            <div class="cal-day-detail-body">
              <div class="cal-day-detail-title">{{ ev.title }}</div>
            </div>
            <div class="cal-day-detail-amount">{{ fmtAmount(ev.amount) }}</div>
          </div>
        </div>
        <div v-if="selectedEventDetail" class="cal-day-detail-extra">
          <div v-if="selectedEventDetail.recommended_date" class="cal-day-detail-row">
            <span class="cal-day-detail-label">Fecha recomendada</span>
            <span class="cal-day-detail-value">{{ fmtDateShort(selectedEventDetail.recommended_date) }}</span>
          </div>
          <div class="cal-day-detail-row">
            <span class="cal-day-detail-label">Fecha límite</span>
            <span class="cal-day-detail-value">{{ fmtDateShort(selectedEventDetail.due_date) }}</span>
          </div>
          <button
            v-if="selectedEventDetail.obligation_id"
            class="cal-day-detail-link"
            @click="$emit('showObligationInfo', selectedEventDetail.obligation_id)"
          >
            Ver deuda
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  TrendingUp, Target, CreditCard, Wallet, Bell,
} from 'lucide-vue-next'
import { useCalendarStore } from '@/stores/useCalendar'
import { useCalendarNavigation } from '@/composables/useCalendarNavigation'
import { useCalendarFilters } from '@/composables/useCalendarFilters'
import { eventColor as _eventColor, typeIcon as _typeIcon, fmtDateShort as _fmtDateShort } from '@/composables/useCalendarHelpers'
import CalendarGridView from '@/components/calendar/CalendarGridView.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  selectedEvent: { type: Object, default: null },
})

const emit = defineEmits(['close', 'selectEvent', 'showObligationInfo'])

const store = useCalendarStore()
const { monthLabel, prevMonth, nextMonth, goToday } = useCalendarNavigation()
const { filteredCalendarDays, activeFilter } = useCalendarFilters()

const storeReady = ref(false)
const selectedDate = ref('')
const selectedEvents = ref([])
const selectedEventDetail = ref(null)

function eventColorFn(ev) { return _eventColor(ev) }

function typeIcon(type) { return _typeIcon(type, { TrendingUp, Target, CreditCard, Wallet, Bell }) }

function fmtAmount(amount) {
  const n = Number(amount)
  if (Number.isNaN(n)) return '$0'
  const abs = Math.abs(n).toLocaleString('es-CO')
  return (n < 0 ? '-$' : '$') + abs
}

function fmtDateShort(dateStr) { return _fmtDateShort(dateStr) }

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  const d = new Date(selectedDate.value + 'T00:00:00')
  const todayStr = new Date().toISOString().slice(0, 10)
  if (selectedDate.value === todayStr) return 'HOY'
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' }).toUpperCase()
})

function handleSelectDay(dateStr) {
  selectedDate.value = dateStr
  const dayEvents = (store.events || []).filter(e => e.due_date === dateStr)
  selectedEvents.value = dayEvents
  selectedEventDetail.value = dayEvents.length > 0 ? dayEvents[0] : null
  if (dayEvents.length > 0) {
    emit('selectEvent', dayEvents[0])
  }
}

function handleSelectEvent(ev) {
  selectedEventDetail.value = ev
  if (!selectedDate.value) {
    selectedDate.value = ev.due_date || ''
  }
  if (!selectedEvents.value.length) {
    selectedEvents.value = [ev]
  }
  emit('selectEvent', ev)
}

function handleCreateOnDate(_dateStr) {
  emit('close')
}

watch(() => props.open, async (val) => {
  if (val) {
    storeReady.value = false
    selectedDate.value = ''
    selectedEvents.value = []
    selectedEventDetail.value = null
    await store.fetchRange()
    storeReady.value = true
    if (props.selectedEvent) {
      handleSelectEvent(props.selectedEvent)
    }
  }
})

defineExpose({ handleSelectDay, handleSelectEvent })
</script>

<style scoped>
.cal-sheet-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: var(--z-modal, 300);
  animation: fadeIn 200ms ease;
}
.cal-sheet {
  background: var(--color-neutral-0);
  width: 100%;
  max-width: 980px;
  border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
  padding: var(--spacing-sm) var(--spacing-md) var(--spacing-md);
  max-height: 85vh;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}
.cal-sheet-handle {
  width: 40px;
  height: 4px;
  background: var(--color-neutral-300);
  border-radius: 2px;
  margin: 0 auto;
  flex-shrink: 0;
}

.cal-sheet > :deep(.calendar-grid-view) {
  overflow-y: auto;
  flex-shrink: 1;
  min-height: 0;
}

.cal-day-detail {
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-neutral-200);
  flex-shrink: 0;
  overflow-y: auto;
}
.cal-day-detail-date {
  font-family: var(--font-display);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: var(--spacing-xs);
}
.cal-day-detail-list { display: flex; flex-direction: column; gap: 2px; }
.cal-day-detail-item {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-xs); border-radius: var(--radius-md);
  background: transparent; border: none; cursor: pointer; text-align: left;
  transition: background var(--transition-fast); width: 100%;
}
.cal-day-detail-item:hover { background: var(--color-neutral-50); }
.cal-day-detail-item--active { background: var(--color-neutral-100); }
.cal-day-detail-icon {
  width: 28px; height: 28px; border-radius: var(--radius-md);
  background: var(--color-neutral-100); display: inline-flex; align-items: center; justify-content: center;
  color: var(--color-neutral-600); flex-shrink: 0;
}
.cal-day-detail-body { flex: 1; min-width: 0; }
.cal-day-detail-title {
  font-size: var(--font-size-sm); font-weight: 600; color: var(--color-neutral-800);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.cal-day-detail-amount {
  font-family: var(--font-mono); font-size: var(--font-size-sm-alt); font-weight: 700;
  color: var(--color-neutral-700); white-space: nowrap; flex-shrink: 0;
}
.cal-day-detail-extra {
  margin-top: var(--spacing-sm); padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-neutral-200);
}
.cal-day-detail-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}
.cal-day-detail-label {
  font-size: var(--font-size-3xs);
  color: var(--color-neutral-500);
}
.cal-day-detail-value {
  font-size: var(--font-size-3xs);
  font-weight: 600;
  color: var(--color-neutral-800);
}
.cal-day-detail-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  width: 100%;
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  color: var(--color-primary-600);
  font-size: var(--font-size-sm);
  font-weight: 600;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.cal-day-detail-link:hover { background: var(--color-primary-50); }
.cal-day-detail-link:active { opacity: 0.7; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

@media (max-width: 767px) {
  .cal-sheet {
    padding: var(--spacing-sm);
    max-height: 90vh;
  }
}
</style>

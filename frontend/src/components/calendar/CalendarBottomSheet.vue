<template>
  <div v-if="open" class="cal-sheet-backdrop" @click.self="$emit('close')">
    <div
      class="cal-sheet"
      :class="'cal-sheet--' + heightState"
      role="dialog"
      aria-modal="true"
      aria-label="Agenda financiera"
    >
      <div class="cal-sheet-header">
        <div class="cal-sheet-grip" role="button" aria-label="Cambiar tamaño" tabindex="0" @click="cycleHeight" @keydown.enter="cycleHeight"></div>
        <span class="cal-sheet-title">Agenda</span>
        <button class="cal-sheet-close" aria-label="Cerrar agenda" @click="$emit('close')">
          <X :size="18" />
        </button>
      </div>

      <div class="cal-sheet-body">
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

        <div v-if="selectedDate && selectedEvents.length === 0" class="cal-day-detail-empty">
          <p>No hay movimientos este día.</p>
        </div>

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
              :aria-label="eventAriaLabel(ev)"
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
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { X } from 'lucide-vue-next'
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
const heightState = ref('half')

const PRESETS = ['half', 'mid', 'high', 'full']

function eventColorFn(ev) { return _eventColor(ev) }

function typeIcon(type) { return _typeIcon(type, { TrendingUp, Target, CreditCard, Wallet, Bell }) }

const TYPE_LABELS = {
  income: 'Ingreso',
  expense: 'Gasto',
  debt: 'Pago',
  goal: 'Meta',
}

function eventAriaLabel(ev) {
  const type = TYPE_LABELS[ev.type] || 'Evento'
  return `${type}: ${ev.title}. ${fmtAmount(ev.amount)}`
}

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

function cycleHeight() {
  const idx = PRESETS.indexOf(heightState.value)
  const next = (idx + 1) % PRESETS.length
  heightState.value = PRESETS[next]
  if (heightState.value === 'full') {
    emit('close')
    heightState.value = 'half'
  }
}

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

function close() {
  heightState.value = 'half'
  emit('close')
}

function onKey(e) {
  if (e.key === 'Escape' && props.open) {
    close()
  }
  if (e.key === 'Backspace' && props.open) {
    close()
  }
}

watch(() => props.open, async (val) => {
  if (val) {
    storeReady.value = false
    selectedDate.value = ''
    selectedEvents.value = []
    selectedEventDetail.value = null
    await store.fetchRange()
    storeReady.value = true
    heightState.value = 'half'
    if (props.selectedEvent) {
      handleSelectEvent(props.selectedEvent)
    }
  }
})

onMounted(() => {
  window.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
})

defineExpose({ handleSelectDay, handleSelectEvent, close })
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
  position: relative;
  display: flex;
  flex-direction: column;
  transition: max-height 200ms ease;
}
.cal-sheet--half { max-height: 50vh; }
.cal-sheet--mid { max-height: 65vh; }
.cal-sheet--high { max-height: 80vh; }
.cal-sheet--full { max-height: 95vh; }

.cal-sheet-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 2px 0 var(--spacing-sm);
}
.cal-sheet-grip {
  width: 36px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: var(--radius-full);
  transition: background var(--transition-fast);
}
.cal-sheet-grip::before {
  content: '';
  display: block;
  width: 28px;
  height: 4px;
  border-radius: 2px;
  background: var(--color-neutral-300);
}
.cal-sheet-grip:hover { background: var(--color-neutral-100); }
.cal-sheet-title {
  font-family: var(--font-display);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-neutral-900);
}
.cal-sheet-close {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  border: none;
  background: transparent;
  color: var(--color-neutral-600);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.cal-sheet-close:hover { background: var(--color-neutral-100); }
.cal-sheet-close:active { transform: scale(0.96); }

.cal-sheet-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
.cal-day-detail-empty {
  margin-top: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-sm);
  text-align: center;
  color: var(--color-neutral-500);
  font-size: var(--font-size-sm-alt);
}
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
  }
}
</style>

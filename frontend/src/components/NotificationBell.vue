<template>
  <div class="notification-bell" ref="bellRef">
    <button class="bell-button" @click="toggleDropdown" :aria-label="`Notificaciones (${totalUnread} sin leer)`">
      <Bell :size="20" />
      <span v-if="totalUnread > 0" class="bell-badge">{{ totalUnread > 9 ? '9+' : totalUnread }}</span>
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="notification-dropdown">
        <div class="dropdown-tabs">
          <button
            class="tab-button"
            :class="{ active: activeTab === 'inbox' }"
            @click="switchTab('inbox')"
          >
            Notificaciones
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'upcoming' }"
            @click="switchTab('upcoming')"
          >
            Próximos pagos
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'coach' }"
            @click="switchTab('coach')"
          >
            Coach
          </button>
        </div>

        <template v-if="activeTab === 'inbox'">
          <div class="dropdown-header">
            <h3 class="dropdown-title">Notificaciones</h3>
            <button v-if="unreadCount > 0" class="btn-mark-all" @click="markAllRead">
              Marcar todas leídas
            </button>
          </div>

          <div v-if="loading" class="dropdown-loading">
            <SkeletonLoader v-for="n in 3" :key="n" variant="text" />
          </div>

          <div v-else-if="notifications.length === 0" class="dropdown-empty">
            <BellOff :size="32" />
            <p>No hay notificaciones</p>
          </div>

          <div v-else class="notification-list">
            <div
              v-for="notif in notifications"
              :key="notif.id"
              class="notification-item"
              :class="{ unread: !notif.is_read }"
              @click="handleNotification(notif)"
            >
              <div class="notif-icon" :class="'notif-' + notif.type">
                <AlertCircle v-if="notif.type === 'warning'" :size="16" />
                <CheckCircle v-else-if="notif.type === 'success'" :size="16" />
                <Info v-else :size="16" />
              </div>
              <div class="notif-content">
                <span class="notif-title">{{ notif.title }}</span>
                <span class="notif-message">{{ notif.message }}</span>
                <span class="notif-time">{{ formatTime(notif.created_at) }}</span>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'upcoming'">
          <div class="dropdown-header">
            <h3 class="dropdown-title">Próximos pagos</h3>
          </div>

          <div class="upcoming-filters">
            <button
              v-for="f in upcomingFilters"
              :key="f.value"
              class="filter-chip"
              :class="{ active: upcomingFilter === f.value }"
              @click="upcomingFilter = f.value"
            >
              {{ f.label }}
            </button>
          </div>

          <div v-if="upcomingLoading" class="dropdown-loading">
            <SkeletonLoader v-for="n in 3" :key="n" variant="text" />
          </div>

          <div v-else-if="filteredUpcomingItems.length === 0" class="dropdown-empty">
            <CalendarCheck :size="32" />
            <p>No hay pagos próximos</p>
          </div>

          <div v-else class="notification-list">
            <div
              v-for="item in filteredUpcomingItems"
              :key="item.event_id"
              class="notification-item upcoming-item"
            >
              <div class="notif-icon" :class="'notif-' + levelClass(item.level)">
                <Clock v-if="item.level === 'Hoy'" :size="16" />
                <AlertTriangle v-else-if="item.level === 'Pendiente'" :size="16" />
                <Calendar v-else :size="16" />
              </div>
              <div class="notif-content">
                <span class="notif-title">{{ item.title }}</span>
                <span class="notif-message">
                  {{ item.amountFormatted }} · vence {{ fmtDate(item.due_date) }}
                </span>
                <span class="notif-level">{{ item.level }}</span>
              </div>
              <div class="notif-actions">
                <button class="btn-pay" @click="handlePay(item.event_id)">
                  Registrar pago
                </button>
                <button v-if="item.obligation_id" class="btn-ghost" @click="handleViewObligation(item.obligation_id)">
                  Ver obligación
                </button>
                <button v-else class="btn-ghost" @click="handleMakeRecurrent(item)">
                  Recurrente
                </button>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="dropdown-header">
            <h3 class="dropdown-title">Coach</h3>
          </div>

          <div v-if="suggestionsLoading" class="dropdown-loading">
            <SkeletonLoader v-for="n in 2" :key="n" variant="text" />
          </div>

          <div v-else-if="suggestions.length === 0" class="dropdown-empty">
            <Lightbulb :size="32" />
            <p>No hay sugerencias ahora</p>
          </div>

          <div v-else class="notification-list">
            <div
              v-for="s in suggestions"
              :key="s.name"
              class="notification-item upcoming-item"
            >
              <div class="notif-icon notif-success">
                <Lightbulb :size="16" />
              </div>
              <div class="notif-content">
                <span class="notif-title">{{ s.name }}</span>
                <span class="notif-message">
                  {{ fmtFull(s.amount) }} · día {{ s.anchor_day }} · confianza {{ s.confidence }}%
                </span>
                <span class="notif-level">Sugerencia</span>
              </div>
              <button class="btn-pay" @click="handleAccept(s)">
                Aceptar
              </button>
            </div>
          </div>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { Bell, BellOff, AlertCircle, CheckCircle, Info, Clock, AlertTriangle, Calendar, CalendarCheck, Lightbulb } from 'lucide-vue-next'
import { useNotifications } from '@/composables/useNotifications'
import { useCurrency } from '@/composables/useCurrency'
import { useToast } from '@/composables/useToast'
import { eventsService } from '@/services/events'

const {
  notifications,
  unreadCount,
  loading,
  upcoming,
  upcomingLoading,
  upcomingFilter,
  filteredUpcoming,
  suggestions,
  suggestionsLoading,
  load,
  loadUpcoming,
  loadSuggestions,
  acceptSuggestion,
  markPaid,
  markAllRead,
  markRead,
  useClickOutside,
} = useNotifications()

const { fmtDate, fmtFull } = useCurrency()
const toast = useToast()

const bellRef = ref(null)
const isOpen = ref(false)
const activeTab = ref('inbox')

const upcomingFilters = [
  { label: 'Todos', value: 'all' },
  { label: 'Hoy', value: 'today' },
  { label: 'Esta semana', value: 'esta_semana' },
]

const totalUnread = computed(() => unreadCount.value)

const filteredUpcomingItems = computed(() => filteredUpcoming())

function levelClass(level) {
  if (level === 'Hoy') return 'warning'
  if (level === 'Pendiente') return 'error'
  if (level === 'Mañana') return 'warning'
  if (level === 'Se acerca') return 'warning'
  return 'info'
}

function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'upcoming') {
    loadUpcoming()
  }
  if (tab === 'coach') {
    loadSuggestions()
  }
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    load()
    if (activeTab.value === 'upcoming') {
      loadUpcoming()
    }
    if (activeTab.value === 'coach') {
      loadSuggestions()
    }
  }
}

async function handleAccept(s) {
  try {
    await acceptSuggestion(s)
    toast?.success('Obligación creada')
  } catch (e) {
    console.error('No pudimos aceptar la sugerencia', e)
  }
}

async function handlePay(eventId) {
  try {
    await markPaid(eventId)
  } catch (e) {
    console.error('No pudimos registrar el pago', e)
  }
}

function handleViewObligation(obligationId) {
  toast?.info('Función en desarrollo')
}

async function handleMakeRecurrent(item) {
  try {
    await eventsService.createObligationFromEvent({
      event_id: item.event_id,
    })
    toast?.success('Obligación recurrente creada')
    await loadUpcoming()
  } catch (e) {
    console.error('No pudimos crear la obligación', e)
  }
}

function handleNotification(notif) {
  markRead(notif)
  isOpen.value = false
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Ahora'
  if (minutes < 60) return `Hace ${minutes}m`
  if (hours < 24) return `Hace ${hours}h`
  if (days < 7) return `Hace ${days}d`
  return date.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' })
}

useClickOutside(bellRef, isOpen)
onMounted(load)
</script>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-button {
  position: relative;
  background: transparent;
  border: none;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--color-neutral-500);
  transition: all var(--transition-fast);
}

.bell-button:hover {
  background: var(--color-neutral-100);
  color: var(--color-neutral-900);
}

.bell-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 18px;
  height: 18px;
  background: var(--color-error-500);
  color: white;
  font-size: 0.6875rem;
  font-weight: 700;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 340px;
  max-height: 480px;
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-modal);
  overflow: hidden;
}

.dropdown-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-neutral-200);
}

.tab-button {
  flex: 1;
  padding: 10px 12px;
  border: none;
  background: transparent;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-neutral-500);
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab-button.active {
  color: var(--color-primary-600);
  border-bottom-color: var(--color-primary-600);
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-neutral-200);
}

.dropdown-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-neutral-900);
}

.btn-mark-all {
  background: none;
  border: none;
  color: var(--color-primary-600);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-mark-all:hover {
  text-decoration: underline;
}

.upcoming-filters {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-neutral-200);
  overflow-x: auto;
}

.filter-chip {
  border: 1px solid var(--color-neutral-200);
  background: var(--color-neutral-0);
  color: var(--color-neutral-700);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.75rem;
  cursor: pointer;
  white-space: nowrap;
}

.filter-chip.active {
  background: var(--color-primary-600);
  border-color: var(--color-primary-600);
  color: white;
}

.dropdown-loading,
.dropdown-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 16px;
  color: var(--color-neutral-500);
  font-size: 0.875rem;
}

.notification-list {
  max-height: 340px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background var(--transition-fast);
  align-items: center;
}

.notification-item:hover {
  background: var(--color-neutral-50);
}

.notification-item.unread {
  background: var(--color-primary-50);
}

.upcoming-item {
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.notif-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.btn-ghost {
  border: 1px solid var(--color-neutral-200);
  background: transparent;
  color: var(--color-neutral-700);
  border-radius: var(--radius-md);
  padding: 6px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-ghost:hover {
  background: var(--color-neutral-50);
}

.notif-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notif-warning {
  background: var(--color-warning-50);
  color: var(--color-warning-600);
}

.notif-success {
  background: var(--color-success-50);
  color: var(--color-success-600);
}

.notif-info {
  background: var(--color-info-50);
  color: var(--color-info-600);
}

.notif-error {
  background: var(--color-error-50);
  color: var(--color-error-600);
}

.notif-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.notif-title {
  font-weight: 600;
  font-size: 0.8125rem;
  color: var(--color-neutral-900);
}

.notif-message {
  font-size: 0.75rem;
  color: var(--color-neutral-500);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notif-time,
.notif-level {
  font-size: 0.6875rem;
  color: var(--color-neutral-400);
}

.btn-pay {
  border: 1px solid var(--color-primary-600);
  background: var(--color-primary-600);
  color: white;
  border-radius: var(--radius-md);
  padding: 6px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-pay:hover {
  background: var(--color-primary-700);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 200ms ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>

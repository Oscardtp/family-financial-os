<template>
  <div class="home-page">
    <div class="home-header">
      <div>
        <h1 class="home-greeting">{{ greeting }}</h1>
        <p class="home-date">{{ todayLabel }}</p>
      </div>
    </div>

    <div v-if="loading" class="home-loading">
      <div class="skeleton-card"></div>
      <div class="skeleton-card"></div>
    </div>

    <template v-else>
      <div class="available-card">
        <span class="available-label">Disponible</span>
        <span class="available-value">${{ fmt(availability?.projected_available ?? 0) }}</span>
        <div class="available-meta">
          <span>Cuentas: ${{ fmt(availability?.available ?? 0) }}</span>
          <span>Pagos: ${{ fmt(availability?.upcoming_payments ?? 0) }}</span>
        </div>
      </div>

      <div class="home-grid">
        <div class="home-col">
          <section class="home-section">
            <h2 class="section-title">📅 Hoy</h2>
            <div v-if="todayEvents.length === 0" class="empty-msg">Nada que pagar 🎉</div>
            <div v-else class="event-list">
              <div v-for="ev in todayEvents" :key="ev.id" class="event-item" :class="eventColor(ev)" @click="goEvent(ev)">
                <span class="ev-item-title">{{ ev.title }}</span>
                <span class="ev-item-amount">{{ fmtFull(ev.amount) }}</span>
                <span class="ev-item-meta">{{ ev.type === 'income' ? 'Ingreso' : 'Pago' }}</span>
              </div>
            </div>
          </section>

          <section class="home-section">
            <h2 class="section-title">🔔 Próximamente</h2>
            <div v-if="upcomingEvents.length === 0" class="empty-msg">No hay pagos próximos</div>
            <div v-else class="event-list">
              <div v-for="ev in upcomingEvents" :key="ev.id" class="event-item" :class="eventColor(ev)" @click="goEvent(ev)">
                <span class="ev-item-title">{{ ev.title }}</span>
                <span class="ev-item-amount">{{ fmtFull(ev.amount) }}</span>
                <span class="ev-item-meta">vence en {{ daysUntil(ev.due_date) }} días</span>
              </div>
            </div>
          </section>
        </div>

        <div class="home-col">
          <section class="home-section">
            <h2 class="section-title">📊 Este mes</h2>
            <div class="month-grid">
              <div class="month-row">
                <span>Ingresos</span>
                <strong class="income">${{ fmt(monthSummary?.expected_income ?? 0) }}</strong>
              </div>
              <div class="month-row">
                <span>Gastos</span>
                <strong class="expense">${{ fmt(monthSummary?.expected_expenses ?? 0) }}</strong>
              </div>
              <div class="month-divider"></div>
              <div class="month-row">
                <span>Disponible proyectado</span>
                <strong :class="(monthSummary?.projected_available ?? 0) < 0 ? 'expense' : 'income'">${{ fmt(monthSummary?.projected_available ?? 0) }}</strong>
              </div>
              <div class="month-row">
                <span>Efectivo necesario</span>
                <strong class="warn">${{ fmt(monthSummary?.cash_needed ?? 0) }}</strong>
              </div>
            </div>
          </section>

          <section class="home-section">
            <h2 class="section-title">🧠 Family Coach</h2>
            <div v-if="suggestions.length === 0" class="empty-msg">No hay sugerencias ahora</div>
            <div v-else class="coach-list">
              <div v-for="s in suggestions" :key="s.name" class="coach-item">
                <p class="coach-text">{{ coachMessage(s) }}</p>
                <button class="coach-btn" @click="acceptSuggestion(s)">Agregar al calendario</button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCalendarStore } from '@/stores/useCalendar'
import { useNotifications } from '@/composables/useNotifications'
import { useCurrency } from '@/composables/useCurrency'
import { eventsService } from '@/services/events'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const store = useCalendarStore()
const { fmt, fmtFull, fmtDate } = useCurrency()
const { suggestions, loadSuggestions, acceptSuggestion } = useNotifications()
const toast = useToast()

const loading = ref(true)
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

async function loadData() {
  loading.value = true
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
    monthSummary.value = null
    todayEvents.value = []
    upcomingEvents.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  loadSuggestions()
})
</script>

<style scoped>
.home-page { max-width: 1100px; margin: 0 auto; padding: 16px; }
.home-header { margin-bottom: 16px; }
.home-greeting { font-family: var(--font-display); font-size: 1.4rem; font-weight: 700; margin: 0; }
.home-date { color: var(--color-neutral-500); font-size: 0.85rem; margin: 4px 0 0; }
.home-loading { display: flex; flex-direction: column; gap: 12px; }
.skeleton-card { height: 80px; background: var(--skeleton, #eef0f3); border-radius: 16px; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

.available-card {
  background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff;
  border-radius: 20px; padding: 20px; margin-bottom: 16px;
  display: flex; flex-direction: column; gap: 6px;
}
.available-label { font-size: 0.8rem; opacity: 0.85; }
.available-value { font-size: 2rem; font-weight: 800; font-family: var(--font-mono); }
.available-meta { display: flex; gap: 12px; font-size: 0.75rem; opacity: 0.8; }

.home-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 768px) { .home-grid { grid-template-columns: 1fr; } }

.home-section {
  background: var(--surface, #fff); border: 1px solid var(--border, #e5e7eb);
  border-radius: 16px; padding: 16px; margin-bottom: 12px;
}
.section-title { font-family: var(--font-display); font-size: 0.9rem; font-weight: 700; margin: 0 0 12px; }
.empty-msg { color: var(--color-neutral-500); font-size: 0.85rem; text-align: center; padding: 24px 0; }

.event-list { display: flex; flex-direction: column; gap: 8px; }
.event-item {
  display: flex; align-items: center; gap: 8px; padding: 10px 12px;
  border-radius: 12px; cursor: pointer; transition: background 150ms;
}
.event-item:hover { filter: brightness(0.97); }
.ev-item-title { font-size: 0.85rem; font-weight: 600; flex: 1; }
.ev-item-amount { font-size: 0.85rem; font-weight: 700; font-family: var(--font-mono); }
.ev-item-meta { font-size: 0.7rem; color: var(--color-neutral-500); white-space: nowrap; }

.ev-green { background: #dcfce7; }
.ev-yellow { background: #fef9c3; }
.ev-red { background: #fee2e2; }
.ev-blue { background: #dbeafe; }
.ev-purple { background: #f3e8ff; }

.month-grid { display: flex; flex-direction: column; gap: 10px; }
.month-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
.month-divider { height: 1px; background: var(--border, #e5e7eb); margin: 4px 0; }
.income { color: #15803d; }
.expense { color: #b91c1c; }
.warn { color: #a16207; }

.coach-list { display: flex; flex-direction: column; gap: 10px; }
.coach-item {
  background: var(--hover, #f3f4f6); border-radius: 12px; padding: 12px;
  display: flex; flex-direction: column; gap: 10px;
}
.coach-text { font-size: 0.82rem; color: var(--color-neutral-700); margin: 0; }
.coach-btn {
  align-self: flex-start; border: none; background: var(--primary, #2563eb); color: #fff;
  padding: 8px 14px; border-radius: 10px; font-size: 0.8rem; font-weight: 600; cursor: pointer;
}
</style>

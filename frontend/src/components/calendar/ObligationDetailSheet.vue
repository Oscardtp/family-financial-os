<template>
  <div v-if="show" class="sheet-backdrop" @click.self="$emit('close')">
    <div class="sheet">
      <button class="sheet-close" @click="$emit('close')" aria-label="Cerrar"><X :size="18" /></button>
      <h3 class="sheet-title">Obligación</h3>

      <div v-if="loading" class="loading-state">
        <p>Cargando...</p>
      </div>

      <div v-else-if="obligation" class="obligation-detail">
        <div class="obligation-header">
          <span class="obligation-name">{{ obligation.name }}</span>
          <span class="obligation-badge" :class="obligation.is_active ? 'badge-active' : 'badge-inactive'">
            {{ obligation.is_active ? 'Activa' : 'Inactiva' }}
          </span>
        </div>

        <div class="obligation-amount">
          {{ fmtFull(obligation.amount) }}<span class="obligation-period">/mes</span>
        </div>

        <div class="obligation-info">
          <div class="obligation-info-row">
            <span class="obligation-label">Paga cada</span>
            <span class="obligation-value">Día {{ obligation.anchor_day }} de cada mes</span>
          </div>
          <div class="obligation-info-row" v-if="obligation.account_id">
            <span class="obligation-label">Se paga desde</span>
            <span class="obligation-value">{{ accountName(obligation.account_id) }}</span>
          </div>
          <div class="obligation-info-row" v-if="obligation.notes">
            <span class="obligation-label">Nota</span>
            <span class="obligation-value">{{ obligation.notes }}</span>
          </div>
        </div>
      </div>

      <div v-else class="empty-state-inline">
        <p>No pudimos cargar esta obligación.</p>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-ghost" @click="$emit('close')">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import { useCalendarStore } from '@/stores/useCalendar'
import { obligationsService } from '@/services/events'

const props = defineProps({
  show: { type: Boolean, default: false },
  obligationId: { type: String, default: '' }
})

const emit = defineEmits(['close'])

const { fmtFull } = useCurrency()
const calendarStore = useCalendarStore()

const obligation = ref(null)
const loading = ref(false)

function accountName(id) {
  const a = calendarStore.accounts.find(x => x.id === id)
  return a ? a.name : id
}

watch(() => props.show, async (val) => {
  if (val && props.obligationId) {
    loading.value = true
    obligation.value = null
    try {
      const res = await obligationsService.get(props.obligationId)
      obligation.value = res.data
    } catch {
      obligation.value = null
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.sheet-backdrop {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4);
  display: flex; align-items: flex-end; justify-content: center; z-index: var(--z-modal);
}
.sheet {
  background: var(--color-neutral-0); width: 100%; max-width: 460px;
  border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
  padding: var(--spacing-lg); position: relative; max-height: 88vh; overflow: auto;
}
.sheet-close { position: absolute; top: var(--spacing-sm); right: var(--spacing-md); border: none; background: transparent; cursor: pointer; color: var(--color-neutral-500); }
.sheet-title { font-family: var(--font-display, 'Poppins', 'Inter', sans-serif); font-size: 1.1rem; font-weight: 700; color: var(--color-neutral-900); text-align: center; padding: var(--spacing-md) var(--spacing-lg) var(--spacing-lg); margin: 0; }
.loading-state { text-align: center; color: var(--color-neutral-500); padding: var(--spacing-lg); }
.empty-state-inline { text-align: center; color: var(--color-neutral-400); font-size: 0.85rem; padding: var(--spacing-lg); }
.obligation-detail { display: flex; flex-direction: column; gap: var(--spacing-md); padding: 0 var(--spacing-sm); }
.obligation-header { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-sm); }
.obligation-name { font-size: 1.1rem; font-weight: 700; color: var(--color-neutral-900); }
.obligation-badge { padding: 4px 10px; border-radius: var(--radius-full); font-size: 0.75rem; font-weight: 600; }
.badge-active { background: var(--color-success-50); color: var(--color-success-700); border: 1px solid var(--color-success-200); }
.badge-inactive { background: var(--color-neutral-100); color: var(--color-neutral-500); border: 1px solid var(--color-neutral-200); }
.obligation-amount { font-family: var(--font-display, 'Poppins', 'Inter', sans-serif); font-size: 1.6rem; font-weight: 800; color: var(--color-neutral-900); }
.obligation-period { font-size: 0.9rem; font-weight: 500; color: var(--color-neutral-500); margin-left: 4px; }
.obligation-info { display: flex; flex-direction: column; gap: var(--spacing-sm); border-top: 1px solid var(--color-neutral-100); padding-top: var(--spacing-md); }
.obligation-info-row { display: flex; justify-content: space-between; align-items: center; }
.obligation-label { color: var(--color-neutral-500); font-size: 0.85rem; }
.obligation-value { color: var(--color-neutral-800); font-size: 0.85rem; font-weight: 600; }
.form-actions { display: flex; gap: var(--spacing-sm); padding: var(--spacing-md) var(--spacing-lg) 0; }
.btn-ghost {
  flex: 1; border: 1.5px solid var(--color-neutral-200); background: var(--color-neutral-0);
  border-radius: var(--radius-lg); padding: var(--spacing-md); font-weight: 600; cursor: pointer;
  color: var(--color-neutral-700);
}
</style>

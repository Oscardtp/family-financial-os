<template>
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
        <div v-if="store.selectedEvent.notes" class="sheet-note">
          {{ store.selectedEvent.notes }}
        </div>
        <div v-if="store.selectedEvent.confidence < 100" class="sheet-row">
          <Info :size="16" /><span>Origen</span>
          <strong>{{ confidenceLabel(store.selectedEvent) }}</strong>
        </div>

        <button
          v-if="store.selectedEvent.status !== 'paid'"
          class="pay-btn"
          @click="$emit('pay', store.selectedEvent)"
        >
          <Check :size="18" /> Marcar como pagado
        </button>
        <button
          v-else
          class="unpay-btn"
          @click="$emit('unpay', store.selectedEvent)"
        >
          <Undo2 :size="18" /> Anular pago
        </button>

        <div class="sheet-divider"></div>

        <button class="edit-btn" @click="$emit('edit', store.selectedEvent)">
          <Pencil :size="16" /> Editar
        </button>
        <button class="delete-btn" @click="$emit('delete', store.selectedEvent)">
          <Trash2 :size="16" /> Eliminar
        </button>

        <button
          v-if="store.selectedEvent.obligation_id"
          class="link-btn"
          @click="$emit('showObligationInfo', store.selectedEvent.obligation_id)"
        >
          Ver obligación <ArrowRight :size="15" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Check, X, ArrowRight, CalendarDays, Clock, User,
  AlertTriangle, PiggyBank, Info, Pencil, Trash2, Wallet,
  TrendingUp, Target, CreditCard, Bell, Undo2,
} from 'lucide-vue-next'
import { useCalendarStore } from '@/stores/useCalendar'
import { useCurrency } from '@/composables/useCurrency'
import {
  statusLabel as _statusLabel,
  statusClass as _statusClass,
  methodLabel as _methodLabel,
  typeIcon as _typeIcon,
  confidenceLabel as _confidenceLabel,
} from '@/composables/useCalendarHelpers'

const store = useCalendarStore()
const { fmtFull, fmtDate } = useCurrency()

function statusLabel(ev) { return _statusLabel(ev) }
function statusClass(ev) { return _statusClass(ev) }
function methodLabel(m) { return _methodLabel(m) }
function typeIcon(type) { return _typeIcon(type, { TrendingUp, Target, CreditCard, Wallet, Bell }) }
function confidenceLabel(ev) { return _confidenceLabel(ev) }

function accountName(id) {
  const a = store.accounts.find(x => x.id === id)
  return a ? a.name : id
}

function memberName(id) {
  const m = store.members.find(x => x.id === id)
  return m ? m.name : id
}

defineEmits(['pay', 'unpay', 'edit', 'delete', 'showObligationInfo'])
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
.sheet-close { position: absolute; top: 14px; right: 14px; border: none; background: transparent; cursor: pointer; color: var(--color-neutral-500); }
.sheet-head { display: flex; align-items: center; gap: var(--spacing-sm); }
.sheet-head h3 { margin: 0; }
.sheet-amount { font-size: 1.6rem; font-weight: 800; margin: var(--spacing-sm) 0 var(--spacing-md); }
.sheet-row { display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-sm) 0; border-bottom: 1.5px solid var(--color-neutral-100); }
.sheet-row span { color: var(--color-neutral-500); margin-right: auto; }
.sheet-row-ok { border-left: 3px solid var(--color-success-500); padding-left: var(--spacing-sm); }
.sheet-row-warn { border-left: 3px solid var(--color-warning-500); padding-left: var(--spacing-sm); }
.sheet-note {
  background: var(--color-warning-50); border-left: 3px solid var(--color-warning-500);
  padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md);
  margin: var(--spacing-sm) 0; font-size: 0.82rem;
}
.pay-btn {
  width: 100%; margin-top: var(--spacing-md); border: none;
  background: var(--color-primary-500); color: #fff;
  padding: var(--spacing-md); border-radius: var(--radius-lg); font-weight: 700;
  cursor: pointer; display: flex; gap: 6px; justify-content: center;
}
.unpay-btn {
  width: 100%; margin-top: var(--spacing-md); border: 1.5px solid var(--color-warning-200);
  background: var(--color-warning-50); color: var(--color-warning-700);
  padding: var(--spacing-md); border-radius: var(--radius-lg); font-weight: 700;
  cursor: pointer; display: flex; gap: 6px; justify-content: center;
  transition: background var(--transition-fast);
}
.unpay-btn:hover { background: var(--color-warning-100); }
.link-btn {
  width: 100%; margin-top: var(--spacing-sm); border: none; background: transparent;
  color: var(--color-primary-500); cursor: pointer; font-weight: 600;
  display: flex; gap: 4px; justify-content: center; align-items: center;
}
.sheet-divider { height: 1.5px; background: var(--color-neutral-200); margin: var(--spacing-md) 0; }
.edit-btn {
  width: 100%; margin-top: var(--spacing-xs); border: none; background: transparent;
  color: var(--color-primary-500); padding: var(--spacing-sm); border-radius: var(--radius-lg);
  font-weight: 600; cursor: pointer; display: flex; gap: 6px; justify-content: center; align-items: center;
  transition: background var(--transition-fast);
}
.edit-btn:hover { background: var(--color-primary-50); }
.delete-btn {
  width: 100%; margin-top: var(--spacing-xs); border: none; background: transparent;
  color: var(--color-error-500); padding: var(--spacing-sm); border-radius: var(--radius-lg);
  font-weight: 600; cursor: pointer; display: flex; gap: 6px; justify-content: center; align-items: center;
  transition: background var(--transition-fast);
}
.delete-btn:hover { background: var(--color-error-50); }
.st-green { color: var(--color-success-700); }
.st-yellow { color: var(--color-warning-700); }
.st-red { color: var(--color-error-700); }
</style>

<template>
  <div v-if="recurrentesOpen" class="sheet-backdrop" @click.self="closeRecurrentes">
    <div class="sheet">
      <button class="sheet-close" @click="closeRecurrentes" aria-label="Cerrar"><X :size="20" /></button>
      <h3 class="form-title">Recurrentes</h3>

      <div v-if="store.obligations.length === 0" class="empty-state-inline">
        <p>No tienes pagos recurrentes todavía.</p>
        <p class="empty-desc">Crea uno desde el botón de agregar rápido.</p>
      </div>

      <div v-else class="recurring-list">
        <div
          v-for="ob in store.obligations"
          :key="ob.id"
          class="recurring-card"
        >
          <div class="recurring-info">
            <span class="recurring-name">{{ ob.name }}</span>
            <span class="recurring-meta">{{ fmtFull(ob.amount) }}/mes · Día {{ ob.anchor_day }}</span>
          </div>
          <button
            class="status-toggle"
            :class="{ active: ob.is_active }"
            @click="onToggleObligation(ob)"
          >
            {{ ob.is_active ? 'Activo' : 'Inactivo' }}
          </button>
        </div>
      </div>

      <button class="add-recurring-btn" @click="showRecurringForm = !showRecurringForm">
        <Plus :size="16" /> Agregar recurrente
      </button>

      <div v-if="showRecurringForm" class="recurring-form">
        <input
          v-model="newRecurring.name"
          class="form-input"
          placeholder="Nombre (ej. Netflix, Arriendo)"
          maxlength="255"
        />
        <input
          v-model.number="newRecurring.amount"
          class="form-input"
          type="number"
          placeholder="Monto"
          min="1"
        />
        <select v-model="newRecurring.account_id" class="form-input">
          <option value="" disabled>Seleccionar cuenta</option>
          <option
            v-for="a in store.accounts"
            :key="a.id"
            :value="a.id"
          >{{ a.name }}</option>
        </select>
        <div class="form-row">
          <input
            v-model.number="newRecurring.day_of_month"
            class="form-input form-input-sm"
            type="number"
            min="1"
            max="31"
            placeholder="Día"
          />
          <input
            v-model="newRecurring.next_due_date"
            class="form-input form-input-sm"
            type="date"
          />
        </div>
        <div class="form-actions">
          <button
            type="button"
            class="primary-btn"
            :disabled="!newRecurring.name || !newRecurring.amount || !newRecurring.account_id || !newRecurring.next_due_date || recurringSaving"
            @click="onCreateRecurring"
          >
            {{ recurringSaving ? 'Guardando...' : 'Guardar' }}
          </button>
          <button type="button" class="ghost-btn" @click="showRecurringForm = false">Cancelar</button>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="ghost-btn" @click="closeRecurrentes">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { X, Plus } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import { useRecurringPayments } from '@/composables/useRecurringPayments'

const { fmtFull } = useCurrency()

const {
  store, recurrentesOpen, showRecurringForm, recurringSaving, newRecurring,
  closeRecurrentes, onCreateRecurring, onToggleObligation,
} = useRecurringPayments()
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
.form-title { margin: 0 0 var(--spacing-md); }
.empty-state-inline { text-align: center; color: var(--color-neutral-400); font-size: 0.85rem; }
.empty-desc { font-size: 0.82rem; color: var(--color-neutral-400); }
.recurring-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.recurring-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md); border: 1.5px solid var(--color-neutral-200);
  border-radius: var(--radius-lg); background: var(--color-neutral-0);
}
.recurring-info { display: flex; flex-direction: column; gap: 2px; }
.recurring-name { font-weight: 700; font-size: 0.9rem; color: var(--color-neutral-800); }
.recurring-meta { font-size: 0.8rem; color: var(--color-neutral-500); }
.status-toggle {
  padding: 5px 12px; border-radius: var(--radius-full); font-size: 0.78rem;
  font-weight: 600; border: 1.5px solid var(--color-neutral-200); background: var(--color-neutral-0);
  color: var(--color-neutral-500); cursor: pointer; transition: all var(--transition-fast);
}
.status-toggle.active {
  border-color: var(--color-success-500); background: var(--color-success-50); color: var(--color-success-700);
}
.status-toggle:hover { border-color: var(--color-neutral-300); }
.add-recurring-btn {
  display: flex; align-items: center; gap: 6px; margin-top: var(--spacing-md);
  border: 1.5px dashed var(--color-neutral-300); background: transparent;
  border-radius: var(--radius-lg); padding: var(--spacing-sm) var(--spacing-md);
  font-weight: 600; font-size: 0.85rem; color: var(--color-primary-500);
  cursor: pointer; width: 100%; justify-content: center;
  transition: all var(--transition-fast);
}
.add-recurring-btn:hover { border-color: var(--color-primary-400); background: var(--color-primary-50); }
.recurring-form { margin-top: var(--spacing-md); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.form-input {
  width: 100%; padding: var(--spacing-sm) var(--spacing-md);
  border: 1.5px solid var(--color-neutral-200); border-radius: var(--radius-lg);
  font-size: 0.85rem; background: var(--color-neutral-0); color: var(--color-neutral-800);
  outline: none; transition: border-color var(--transition-fast);
}
.form-input:focus { border-color: var(--color-primary-500); }
.form-input-sm { flex: 1; }
.form-row { display: flex; gap: var(--spacing-sm); }
.form-actions { display: flex; gap: var(--spacing-sm); margin-top: var(--spacing-md); }
.primary-btn {
  flex: 1; border: none; background: var(--color-primary-500); color: #fff;
  padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-lg);
  font-weight: 600; cursor: pointer; transition: background var(--transition-fast);
}
.primary-btn:hover:not(:disabled) { background: var(--color-primary-600); }
.primary-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.ghost-btn {
  flex: 1; border: 1.5px solid var(--color-neutral-200); background: var(--color-neutral-0);
  border-radius: var(--radius-lg); padding: var(--spacing-md); font-weight: 600; cursor: pointer;
  color: var(--color-neutral-700);
}
</style>

<template>
  <div class="debt-actions">
    <button
      v-if="debt.status === 'active'"
      class="action-btn secondary"
      @click="$emit('edit', debt)"
    >
      <Pencil :size="14" />
      Editar
    </button>
    <button
      v-if="debt.status === 'active'"
      class="action-btn primary"
      @click="$emit('pay', debt)"
    >
      <DollarSign :size="14" />
      Pagar
    </button>
    <button
      class="action-btn secondary"
      @click="$emit('amortization', debt.id)"
    >
      <Table2 :size="14" />
      Amortización
    </button>
    <button
      v-if="debt.status === 'active'"
      class="action-btn warning"
      @click="$emit('deactivate', debt)"
    >
      <Pause :size="14" />
      Pausar
    </button>
    <button
      v-else-if="debt.status === 'paused' && debt.current_balance > 0"
      class="action-btn success"
      @click="$emit('activate', debt)"
    >
      <Play :size="14" />
      Activar
    </button>
    <button
      v-else-if="debt.status === 'paid_off'"
      class="action-btn success"
      @click="$emit('reactivate', debt)"
    >
      <RotateCcw :size="14" />
      Reactivar
    </button>
    <button
      class="action-btn danger"
      @click="$emit('request-delete', debt)"
    >
      <Trash2 :size="14" />
      Eliminar
    </button>
  </div>
</template>

<script setup>
import { Pencil, DollarSign, Table2, Pause, Play, Trash2, RotateCcw } from 'lucide-vue-next'

defineProps({
  debt: { type: Object, required: true },
})

defineEmits(['edit', 'pay', 'amortization', 'deactivate', 'activate', 'reactivate', 'request-delete'])
</script>

<style scoped>
.debt-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--color-neutral-0);
  color: var(--color-neutral-700);
}

.action-btn:hover {
  background: var(--color-neutral-100);
}

.action-btn.primary {
  background: var(--color-primary-500);
  color: white;
  border-color: var(--color-primary-500);
}

.action-btn.primary:hover {
  background: var(--color-primary-600);
}

.action-btn.warning {
  color: var(--color-warning-600);
  border-color: var(--color-warning-200);
}

.action-btn.warning:hover {
  background: var(--color-warning-50);
}

.action-btn.success {
  color: var(--color-success-600);
  border-color: var(--color-success-200);
}

.action-btn.success:hover {
  background: var(--color-success-50);
}

.action-btn.danger {
  color: var(--color-error-600);
  border-color: var(--color-error-200);
}

.action-btn.danger:hover {
  background: var(--color-error-50);
}
</style>

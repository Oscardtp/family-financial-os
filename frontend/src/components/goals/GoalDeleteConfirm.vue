<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')" @keydown.escape="$emit('close')" role="alertdialog" aria-modal="true" aria-label="Confirmar eliminación">
    <div class="modal-content modal-small" @click.stop>
      <h3 class="modal-title">¿Eliminar "{{ goal?.name }}"?</h3>
      <p class="delete-warning">No se puede deshacer. Se borrarán todos los aportes que registraste.</p>
      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
        <button class="btn-confirm btn-danger" @click="$emit('confirm')" :disabled="deleting">
          {{ deleting ? 'Eliminando...' : 'Eliminar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  goal: { type: Object, default: null },
  deleting: { type: Boolean, default: false },
})

defineEmits(['close', 'confirm'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: 24px;
  width: 90%;
  max-width: 360px;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--color-neutral-900);
}

.delete-warning {
  font-size: 0.875rem;
  color: var(--color-neutral-600);
  margin: 0;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}

.btn-cancel {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
  padding: 8px 20px;
  border-radius: var(--radius-pill);
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  background: var(--color-neutral-200);
}

.btn-confirm {
  background: var(--color-primary-500);
  color: white;
  padding: 8px 20px;
  border-radius: var(--radius-pill);
  border: none;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.btn-confirm:disabled {
  background: var(--color-primary-300);
  cursor: not-allowed;
}

.btn-confirm.btn-danger {
  background: var(--color-error-500);
}

.btn-confirm.btn-danger:hover {
  background: var(--color-error-600);
}
</style>

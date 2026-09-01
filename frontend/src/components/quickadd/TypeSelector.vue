<template>
  <div class="type-selector">
    <button class="type-btn expense" @click="$emit('select', 'expense')">
      <span class="type-icon">💸</span>
      <span class="type-label">Pago</span>
      <span class="type-hint">Algo que pagaste</span>
    </button>
    <button class="type-btn income" @click="$emit('select', 'income')">
      <span class="type-icon">💰</span>
      <span class="type-label">Ingreso</span>
      <span class="type-hint">Dinero que recibiste</span>
    </button>
    <button class="type-btn recurring" @click="$emit('select', 'recurring')">
      <span class="type-icon">🔁</span>
      <span class="type-label">Recurrente</span>
      <span class="type-hint">Pago fijo mensual</span>
    </button>
    <button class="type-btn goal" @click="$emit('select', 'goal')">
      <span class="type-icon">🎯</span>
      <span class="type-label">Meta</span>
      <span class="type-hint">Crear meta de ahorro</span>
    </button>
  </div>
</template>

<script setup>
defineEmits(['select'])
</script>

<style scoped>
.type-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.type-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-lg) var(--spacing-sm);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  background: var(--color-neutral-0);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.type-btn:hover {
  border-color: var(--color-primary-300);
  background: var(--color-primary-50);
}

.type-btn.expense:hover { border-color: var(--color-error-300); background: var(--color-error-50); }
.type-btn.income:hover { border-color: var(--color-success-300); background: var(--color-success-50); }
.type-btn.recurring:hover { border-color: var(--color-warning-300); background: var(--color-warning-50); }
.type-btn.goal:hover { border-color: var(--color-info-300); background: var(--color-info-50); }

.type-icon { font-size: 28px; }

.type-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-neutral-800);
}

.type-hint {
  font-size: 11px;
  color: var(--color-neutral-400);
  text-align: center;
  line-height: 1.2;
}

@media (max-width: 640px) {
  .type-btn { padding: var(--spacing-md) var(--spacing-xs); }
  .type-icon { font-size: 24px; }
  .type-hint { display: none; }
}
</style>

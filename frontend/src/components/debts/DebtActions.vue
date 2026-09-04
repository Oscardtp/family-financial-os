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
  </div>
</template>

<script setup>
import { Pencil, DollarSign } from 'lucide-vue-next'

defineProps({
  debt: { type: Object, required: true },
})

defineEmits(['edit', 'pay'])
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
</style>

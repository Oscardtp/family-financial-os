<template>
  <div class="item-card card">
    <h3 class="card-title">{{ title }}</h3>
    <div v-if="items.length" class="item-list">
      <div v-for="item in items" :key="item.id" class="item-row">
        <div class="item-info">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-type">{{ item.type }}</span>
        </div>
        <span class="item-value" :class="valueClass">${{ fmt(valueAccessor(item)) }}</span>
        <div class="item-actions">
          <button class="btn btn-sm btn-outline" @click="$emit('edit', item)">Editar</button>
          <button class="btn btn-sm btn-danger" @click="$emit('delete', item.id)">X</button>
        </div>
      </div>
    </div>
    <p v-else class="empty-text">{{ emptyText }}</p>
  </div>
</template>

<script setup>
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
  valueAccessor: { type: Function, required: true },
  valueClass: { type: String, default: '' },
  emptyText: { type: String, default: 'No hay registros' },
})

defineEmits(['edit', 'delete'])
</script>

<style scoped>
.item-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}
.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: var(--spacing-md);
}
.item-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-neutral-100);
}
.item-row:last-child { border-bottom: none; }
.item-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.item-name { font-weight: 500; font-size: 0.875rem; color: var(--color-neutral-800); }
.item-type { font-size: 0.75rem; color: var(--color-neutral-400); text-transform: capitalize; }
.item-value { font-weight: 600; font-family: var(--font-mono); font-size: 0.875rem; }
.item-value.income { color: var(--color-success-600); }
.item-value.expense { color: var(--color-error-600); }
.item-actions { display: flex; gap: var(--spacing-xs); }
.empty-text { color: var(--color-neutral-400); font-size: 0.875rem; text-align: center; padding: var(--spacing-lg); }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }
.btn-outline {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  color: var(--color-neutral-700);
}
.btn-outline:hover { border-color: var(--color-primary-400); color: var(--color-primary-600); }
.btn-danger { background: var(--color-error-600); color: white; }
.btn-danger:hover { background: var(--color-error-700); }
</style>

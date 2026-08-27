<template>
  <div class="budget-card card-hover">
    <div class="budget-header">
      <span class="budget-name">{{ item.category_icon || '📦' }} {{ item.category }}</span>
      <span class="budget-status" :class="'status-' + item.status">{{ statusLabel(item.status) }}</span>
    </div>
    <div class="budget-bar">
      <div class="budget-fill" :class="'fill-' + item.status" :style="{ width: Math.min(item.percentage, 100) + '%' }" />
    </div>
    <div class="budget-amounts">
      <span>Gastado: ${{ fmt(item.spent) }}</span>
      <span>Podemos: ${{ fmt(item.budgeted) }}</span>
    </div>
    <p class="budget-message" :class="'msg-' + item.status">{{ item.message }}</p>
    <div class="budget-actions">
      <button class="btn btn-sm btn-outline" @click="$emit('edit', item)">Editar</button>
      <button class="btn btn-sm btn-danger" @click="$emit('delete', item)">Eliminar</button>
    </div>
  </div>
</template>

<script setup>
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

defineProps({
  item: { type: Object, required: true },
  statusLabel: { type: Function, required: true },
})

defineEmits(['edit', 'delete'])
</script>

<style scoped>
.budget-card {
  background: var(--color-neutral-0); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); box-shadow: var(--shadow-sm);
}
.budget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-sm); }
.budget-name { font-weight: 600; font-size: 0.9rem; color: var(--color-neutral-900); }
.budget-status { font-size: 0.75rem; font-weight: 500; }
.status-ok { color: var(--color-success-600); }
.status-warning { color: var(--color-warning-600); }
.status-over { color: var(--color-error-600); }
.budget-bar { height: 8px; background: var(--color-neutral-100); border-radius: 999px; overflow: hidden; margin-bottom: var(--spacing-sm); }
.budget-fill { height: 100%; border-radius: 999px; transition: width 300ms ease; }
.fill-ok { background: var(--color-success-500); }
.fill-warning { background: var(--color-warning-500); }
.fill-over { background: var(--color-error-500); }
.budget-amounts { display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--color-neutral-400); margin-bottom: var(--spacing-sm); }
.budget-message { font-size: 0.8rem; line-height: 1.4; padding: var(--spacing-sm); border-radius: var(--radius-md); margin: 0; }
.msg-ok { background: var(--color-success-50); color: var(--color-success-700); }
.msg-warning { background: var(--color-warning-50); color: var(--color-warning-700); }
.msg-over { background: var(--color-error-50); color: var(--color-error-700); }
.budget-actions { display: flex; gap: var(--spacing-sm); margin-top: var(--spacing-sm); }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }
.btn-outline {
  background: var(--color-neutral-0); border: 1px solid var(--color-neutral-200);
  color: var(--color-neutral-700);
}
.btn-outline:hover { border-color: var(--color-primary-400); color: var(--color-primary-600); }
.btn-danger { background: var(--color-error-600); color: white; }
.btn-danger:hover { background: var(--color-error-700); }
</style>

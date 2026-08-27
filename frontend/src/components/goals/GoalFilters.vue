<template>
  <div class="goals-toolbar">
    <div class="filter-group">
      <button
        class="filter-btn"
        :class="{ active: modelFilterType === 'all' }"
        @click="$emit('update:modelFilterType', 'all')"
      >Todas</button>
      <button
        class="filter-btn"
        :class="{ active: modelFilterType === 'savings' }"
        @click="$emit('update:modelFilterType', 'savings')"
      >Ahorro</button>
      <button
        class="filter-btn"
        :class="{ active: modelFilterType === 'investment' }"
        @click="$emit('update:modelFilterType', 'investment')"
      >Inversión</button>
    </div>
    <select :value="modelSortBy" @change="$emit('update:modelSortBy', $event.target.value)" class="sort-select">
      <option value="name">Nombre</option>
      <option value="priority">Prioridad</option>
      <option value="progress">Progreso</option>
      <option value="date">Fecha</option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  modelFilterType: { type: String, default: 'all' },
  modelSortBy: { type: String, default: 'name' },
})

defineEmits(['update:modelFilterType', 'update:modelSortBy'])
</script>

<style scoped>
.goals-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.filter-group {
  display: flex;
  gap: 4px;
  background: var(--color-neutral-100);
  border-radius: var(--radius-pill);
  padding: 3px;
}

.filter-btn {
  padding: 6px 14px;
  border: none;
  border-radius: var(--radius-pill);
  background: transparent;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-neutral-600);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn:hover {
  color: var(--color-neutral-900);
}

.filter-btn.active {
  background: var(--color-neutral-0);
  color: var(--color-neutral-900);
  box-shadow: var(--shadow-xs);
}

.sort-select {
  padding: 6px 12px;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-pill);
  font-size: 0.8125rem;
  color: var(--color-neutral-700);
  background: var(--color-neutral-0);
  cursor: pointer;
}

.sort-select:focus {
  outline: none;
  border-color: var(--color-primary-400);
}

@media (max-width: 480px) {
  .goals-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-group {
    justify-content: center;
  }
  .sort-select {
    align-self: center;
  }
}
</style>

<template>
  <div class="calendar-toolbar">
    <div class="nav-group">
      <button class="btn-today" @click="$emit('today')">Hoy</button>
      <button class="btn-icon" @click="$emit('prev')" aria-label="Mes anterior"><ChevronLeft :size="16" /></button>
      <button class="btn-icon" @click="$emit('next')" aria-label="Mes siguiente"><ChevronRight :size="16" /></button>
      <h2 class="cal-month">{{ monthLabel }}</h2>
    </div>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

defineProps({
  monthLabel: { type: String, required: true },
})
defineEmits(['prev', 'next', 'today'])
</script>

<style scoped>
.calendar-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--color-neutral-200);
  gap: var(--spacing-md); flex-wrap: wrap;
}
.nav-group { display: flex; align-items: center; gap: var(--spacing-sm); }

.btn-today {
  background: var(--color-neutral-100); color: var(--color-neutral-700); border: none;
  padding: 6px 14px; border-radius: var(--radius-sm); font-size: var(--font-size-xs-alt);
  font-weight: 500; cursor: pointer; transition: all var(--transition-fast);
}
.btn-today:hover { background: var(--color-neutral-200); }

.btn-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border: none; background: var(--color-neutral-100);
  border-radius: var(--radius-sm); cursor: pointer; color: var(--color-neutral-700);
  transition: background var(--transition-fast);
}
.btn-icon:hover { background: var(--color-neutral-200); }

.cal-month {
  font-weight: 600; font-size: var(--font-size-base); color: var(--color-neutral-800);
  text-transform: capitalize; min-width: 170px;
}
</style>

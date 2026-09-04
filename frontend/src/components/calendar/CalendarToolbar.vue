<template>
  <div class="cal-toolbar">
    <div class="toolbar-top">
      <div class="view-toggle">
        <button
          class="toggle-btn"
          :class="{ active: viewMode === 'calendar' }"
          @click="$emit('update:viewMode', 'calendar')"
        >
          <CalendarDays :size="16" /> Calendario
        </button>
        <button
          class="toggle-btn"
          :class="{ active: viewMode === 'list' }"
          @click="$emit('update:viewMode', 'list')"
        >
          <List :size="16" /> Lista
        </button>
      </div>
      <button class="link-action" @click="$emit('openRecurrentes')">
        <Repeat :size="15" /> Admin recurrentes <ArrowRight :size="14" />
      </button>
    </div>

    <div class="filter-row">
      <button
        v-for="f in filters"
        :key="f.key"
        class="filter-pill"
        :class="{ active: activeFilter === f.key }"
        :aria-pressed="activeFilter === f.key"
        @click="$emit('update:activeFilter', f.key)"
      >{{ f.label }}</button>
    </div>

    <div class="cal-nav">
      <button class="today-btn" @click="$emit('today')">Hoy</button>
      <button class="nav-btn" @click="$emit('prev')" aria-label="Mes anterior"><ChevronLeft :size="20" /></button>
      <span class="cal-month">{{ monthLabel }}</span>
      <button class="nav-btn" @click="$emit('next')" aria-label="Mes siguiente"><ChevronRight :size="20" /></button>
    </div>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight, ArrowRight, CalendarDays, List, Repeat } from 'lucide-vue-next'

defineProps({
  viewMode: { type: String, required: true },
  activeFilter: { type: String, required: true },
  monthLabel: { type: String, required: true },
  filters: { type: Array, required: true },
})

defineEmits(['update:viewMode', 'update:activeFilter', 'prev', 'next', 'today', 'openRecurrentes'])
</script>

<style scoped>
.cal-toolbar { margin-bottom: var(--spacing-md); }
.toolbar-top { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-sm); margin-bottom: var(--spacing-sm); }
.view-toggle { display: flex; background: var(--color-neutral-100); border-radius: var(--radius-full); padding: 3px; }
.toggle-btn {
  display: flex; align-items: center; gap: 6px; padding: 7px 14px; border: none; border-radius: var(--radius-full);
  background: transparent; font-size: 0.85rem; font-weight: 600; color: var(--color-neutral-500); cursor: pointer;
  transition: all var(--transition-fast);
}
.toggle-btn.active { background: var(--color-neutral-0); color: var(--color-neutral-800); box-shadow: var(--shadow-xs); }
.toggle-btn:hover:not(.active) { color: var(--color-neutral-700); }
.link-action {
  display: flex; align-items: center; gap: 5px; border: none; background: transparent;
  color: var(--color-primary-500); font-size: 0.82rem; font-weight: 600; cursor: pointer;
  transition: color var(--transition-fast);
}
.link-action:hover { color: var(--color-primary-700); }

.filter-row { display: flex; gap: var(--spacing-xs); margin-bottom: var(--spacing-sm); overflow-x: auto; padding-bottom: 2px; }
.filter-pill {
  flex-shrink: 0; padding: 6px 14px; border: 1.5px solid var(--color-neutral-200);
  border-radius: var(--radius-full); background: var(--color-neutral-0); font-size: 0.82rem;
  font-weight: 600; color: var(--color-neutral-500); cursor: pointer;
  transition: all var(--transition-fast);
}
.filter-pill.active {
  border-color: var(--color-primary-500); color: var(--color-primary-600);
  background: var(--color-primary-50);
}
.filter-pill:hover:not(.active) { border-color: var(--color-neutral-300); color: var(--color-neutral-700); }

.cal-nav { display: flex; align-items: center; gap: var(--spacing-sm); }
.today-btn {
  border: 1.5px solid var(--color-neutral-200); background: var(--color-neutral-0);
  border-radius: var(--radius-full); padding: 6px 14px; cursor: pointer; font-weight: 600;
  font-size: 0.85rem; color: var(--color-neutral-700); transition: all var(--transition-fast);
}
.today-btn:hover { border-color: var(--color-primary-300); color: var(--color-primary-600); }
.cal-month { text-transform: capitalize; font-weight: 700; font-size: 1.05rem; min-width: 170px; }
.nav-btn { border: none; background: transparent; cursor: pointer; border-radius: 50%; padding: var(--spacing-xs); color: var(--color-neutral-600); }
.nav-btn:hover { background: var(--color-neutral-100); }
</style>

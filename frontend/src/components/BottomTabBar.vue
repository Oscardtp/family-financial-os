<template>
  <nav class="bottom-tab-bar">
    <router-link
      v-for="tab in tabs"
      :key="tab.to"
      :to="tab.to"
      class="tab-item"
      :class="{ active: $route.path === tab.to }"
    >
      <component :is="tab.icon" :size="20" />
      <span class="tab-label">{{ tab.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { LayoutDashboard, Receipt, Calendar, Target, User } from 'lucide-vue-next'

const route = useRoute()

const tabs = [
  { to: '/', label: 'Inicio', icon: LayoutDashboard },
  { to: '/debts', label: 'Deudas', icon: Receipt },
  { to: '/calendar', label: 'Pagos', icon: Calendar },
  { to: '/goals', label: 'Metas', icon: Target },
  { to: '/config', label: 'Perfil', icon: User },
]
</script>

<style scoped>
.bottom-tab-bar {
  display: none;
}

@media (max-width: 640px) {
  .bottom-tab-bar {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--color-neutral-0);
    border-top: 1px solid var(--color-neutral-200);
    padding: var(--spacing-xs) 0;
    padding-bottom: env(safe-area-inset-bottom, var(--spacing-xs));
    z-index: 100;
    justify-content: space-around;
  }

  [data-theme="dark"] .bottom-tab-bar {
    background: var(--color-neutral-900);
    border-top-color: var(--color-neutral-700);
  }

  .tab-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-md);
    color: var(--color-neutral-500);
    text-decoration: none;
    font-size: 10px;
    font-weight: 500;
    transition: color var(--transition-fast);
    min-width: 50px;
  }

  .tab-item.active {
    color: var(--color-primary-600);
  }

  [data-theme="dark"] .tab-item.active {
    color: var(--color-primary-400);
  }

  .tab-label {
    line-height: 1;
  }
}
</style>

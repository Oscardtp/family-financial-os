<template>
  <div class="app-layout">
    <button
      class="hamburger-btn"
      @click="toggleMobileSidebar"
    >
      <Menu :size="20" />
    </button>
    <div
      v-if="mobileOpen"
      class="sidebar-overlay"
      @click="mobileOpen = false"
    />
    <aside
      class="sidebar"
      :class="{ collapsed: sidebarCollapsed, open: mobileOpen }"
    >
      <div class="sidebar-header">
        <span
          v-if="!sidebarCollapsed"
          class="logo"
        >FF</span>
        <button
          class="collapse-btn"
          @click="toggleSidebar"
        >
          <PanelLeftClose
            v-if="!sidebarCollapsed"
            :size="18"
          />
          <PanelLeftOpen
            v-else
            :size="18"
          />
        </button>
      </div>
      <nav class="sidebar-nav">
        <template v-for="section in navSections" :key="section.label || 'main'">
          <div v-if="section.label && !sidebarCollapsed" class="nav-section-label">
            {{ section.label }}
          </div>
          <router-link
            v-for="item in section.items"
            :key="item.to"
            :to="item.to"
            class="nav-item"
            :class="{ active: $route.path === item.to }"
          >
            <component
              :is="item.icon"
              :size="20"
            />
            <span
              v-if="!sidebarCollapsed"
              class="nav-label"
            >{{ item.label }}</span>
          </router-link>
        </template>
      </nav>
      <div class="sidebar-footer">
        <button
          class="nav-item"
          @click="handleLogout"
        >
          <LogOut :size="20" />
          <span
            v-if="!sidebarCollapsed"
            class="nav-label"
          >Salir</span>
        </button>
      </div>
    </aside>
    <div class="main-area">
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'
import NotificationBell from '@/components/NotificationBell.vue'
import {
  LayoutDashboard, Receipt, Calendar, Target,
  Users, User, PanelLeftClose, PanelLeftOpen,
  LogOut, Menu
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const sidebarCollapsed = ref(false)
const mobileOpen = ref(false)

function handleResize() {
  const w = window.innerWidth
  if (w <= 640) {
    sidebarCollapsed.value = true
  } else if (w <= 1024) {
    sidebarCollapsed.value = true
  } else {
    sidebarCollapsed.value = false
  }
}

function toggleSidebar() {
  const w = window.innerWidth
  if (w <= 640) {
    mobileOpen.value = !mobileOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

function toggleMobileSidebar() {
  mobileOpen.value = !mobileOpen.value
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

const navSections = [
  {
    label: 'DINERO',
    items: [
      { to: '/', label: 'Resumen', icon: LayoutDashboard },
      { to: '/debts', label: 'Mis Deudas', icon: Receipt },
    ]
  },
  {
    label: 'PAGOS',
    items: [
      { to: '/calendar', label: 'Calendario', icon: Calendar },
    ]
  },
  {
    label: 'METAS',
    items: [
      { to: '/goals', label: 'Metas', icon: Target },
    ]
  },
  {
    label: 'HOGAR',
    items: [
      { to: '/household', label: 'Mi Familia', icon: Users },
      { to: '/config', label: 'Mi Perfil', icon: User },
    ]
  },
]

const navItems = navSections.flatMap(s => s.items)

const currentPageTitle = computed(() => {
  const item = navItems.find(i => i.to === route.path)
  return item?.label || 'Inicio'
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}

import { watch } from 'vue'
watch(() => route.path, () => {
  mobileOpen.value = false
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-neutral-50);
}

[data-theme="dark"] .app-layout {
  background: var(--color-neutral-0);
}
.sidebar {
  width: 240px;
  background: var(--color-neutral-800);
  color: var(--color-neutral-900);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal), transform var(--transition-normal);
  flex-shrink: 0;
}
.sidebar.collapsed { width: 60px; }
.sidebar-overlay { display: none; }
.hamburger-btn { display: none; }
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-neutral-700);
}
.logo {
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--color-primary-400);
}
.collapse-btn {
  background: none;
  border: none;
  color: var(--color-neutral-400);
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-sm);
}
.collapse-btn:hover { color: var(--color-neutral-100); background: var(--color-neutral-600); }
.sidebar-nav {
  flex: 1;
  padding: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  color: var(--color-neutral-400);
  text-decoration: none;
  font-size: 0.875rem;
  transition: all var(--transition-fast);
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
}
.nav-item:hover { color: var(--color-neutral-100); background: var(--color-neutral-600); }
.nav-item.active { color: white; background: var(--color-primary-600); }
.nav-section-label {
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--color-neutral-500);
  padding: var(--space-md) var(--space-md) var(--space-xs);
  text-transform: uppercase;
}
.sidebar-footer {
  padding: var(--space-sm);
  border-top: 1px solid var(--color-neutral-700);
}
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.content {
  flex: 1;
  padding: var(--space-xl);
  overflow-y: auto;
}

@media (min-width: 641px) and (max-width: 1024px) {
  .sidebar {
    width: var(--sidebar-collapsed-width);
  }
  .sidebar .nav-label {
    display: none;
  }
  .main-area {
    margin-left: var(--sidebar-collapsed-width);
  }
}

@media (max-width: 640px) {
  .sidebar {
    position: fixed;
    transform: translateX(-100%);
    z-index: var(--z-sidebar);
    width: var(--sidebar-width);
  }
  .sidebar.open {
    transform: translateX(0);
  }
  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: calc(var(--z-sidebar) - 1);
  }
  .main-area {
    margin-left: 0;
  }
  .hamburger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: var(--space-md);
    left: var(--space-md);
    z-index: calc(var(--z-sidebar) - 2);
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    background: var(--color-neutral-800);
    color: white;
    border: none;
    cursor: pointer;
  }
  .content {
    padding: var(--space-md);
  }
}
</style>

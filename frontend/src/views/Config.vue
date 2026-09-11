<template>
  <div class="config-page">
    <h2 class="page-title">Configuración</h2>

    <div class="config-tabs">
      <button v-for="tab in tabs" :key="tab.key" class="tab-btn" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        <component :is="tab.icon" :size="16" />
        {{ tab.label }}
      </button>
    </div>

    <template v-if="activeTab === 'profile'">
      <ProfileTab />
    </template>

    <template v-else-if="activeTab === 'household'">
      <ConfigHouseholdTab />
    </template>

    <template v-else-if="activeTab === 'categories'">
      <CategoriesTab />
    </template>

    <template v-else-if="activeTab === 'accounts'">
      <AccountsTab />
    </template>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { User, Tag, Wallet, Users } from 'lucide-vue-next'
import ConfigHouseholdTab from '@/components/ConfigHouseholdTab.vue'
import CategoriesTab from '@/components/CategoriesTab.vue'
import AccountsTab from '@/components/AccountsTab.vue'
import ProfileTab from '@/components/ProfileTab.vue'

const route = useRoute()

const tabs = [
  { key: 'profile', label: 'Perfil', icon: User },
  { key: 'household', label: 'Hogar', icon: Users },
  { key: 'categories', label: 'Categorías', icon: Tag },
  { key: 'accounts', label: 'Cuentas', icon: Wallet },
]

const activeTab = ref(route.query.tab || 'profile')
watch(() => route.query.tab, (t) => { if (t) activeTab.value = t })
</script>

<style scoped>
.config-page { max-width: 700px; margin: 0 auto; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); margin-bottom: var(--spacing-lg); }

.config-tabs {
  display: flex; gap: var(--spacing-xs); margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-neutral-200); padding-bottom: var(--spacing-xs);
}
.tab-btn {
  display: flex; align-items: center; gap: 6px; padding: var(--spacing-sm) var(--spacing-md);
  border: none; background: none; font-size: 0.85rem; font-weight: 500;
  color: var(--color-neutral-500); cursor: pointer; border-radius: var(--radius-md) var(--radius-md) 0 0;
  transition: all var(--transition-fast); border-bottom: 2px solid transparent;
}
.tab-btn:hover { color: var(--color-neutral-700); }
.tab-btn.active { color: var(--color-primary-600); border-bottom-color: var(--color-primary-600); }

@media (max-width: 640px) {
  .config-tabs { overflow-x: auto; }
}
</style>

<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition
        name="page"
        mode="out-in"
      >
        <component :is="Component" />
      </transition>
    </router-view>
    <BottomTabBar v-if="isAuthenticated" />
    <QuickAddFab
      v-if="isAuthenticated"
      :accounts="accounts"
      :categories="categories"
      :debts="debts"
      @transaction-created="refreshData"
    />
    <ToastNotification />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BottomTabBar from '@/components/BottomTabBar.vue'
import QuickAddFab from '@/components/quickadd/QuickAddFab.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import api from '@/services/api'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const accounts = ref([])
const categories = ref([])
const debts = ref([])

const fetchData = async () => {
  if (!authStore.isAuthenticated) return
  try {
    const [accRes, catRes, debtRes] = await Promise.all([
      api.get('/accounts'),
      api.get('/categories'),
      api.get('/debts'),
    ])
    accounts.value = accRes.data
    categories.value = catRes.data
    debts.value = debtRes.data
  } catch (e) {
    console.error('Failed to load FAB data:', e)
  }
}

const refreshData = () => {
  fetchData()
}

onMounted(fetchData)
watch(() => authStore.isAuthenticated, (val) => {
  if (val) fetchData()
  else { accounts.value = []; categories.value = []; debts.value = [] }
})
</script>

<style>
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--color-neutral-50);
  color: var(--color-neutral-900);
  line-height: 1.6;
}

[data-theme="dark"] body {
  background-color: var(--color-neutral-0);
  color: var(--color-neutral-100);
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 640px) {
  .content {
    padding-bottom: 80px !important;
  }
}
</style>

import { createRouter, createWebHistory } from 'vue-router'

  const routes = [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      component: () => import('@/components/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'Resumen', component: () => import('@/views/Resumen.vue') },
        { path: 'debts', name: 'Debts', component: () => import('@/views/Debts.vue') },
        { path: 'calendar', name: 'Calendar', component: () => import('@/views/Calendar.vue') },
        { path: 'goals', name: 'Goals', component: () => import('@/views/Goals.vue') },
        { path: 'config', name: 'Config', component: () => import('@/views/Config.vue') },
      ],
    },
  ]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) return { name: 'Login' }
  if (to.meta.guest && token) return { name: 'Resumen' }
})

export default router

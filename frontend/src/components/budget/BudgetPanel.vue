<template>
  <div class="budget-panel">
    <div class="bp-header">
      <h3 class="bp-title"><span class="title-icon"><BarChart3 :size="18" /></span> Presupuesto</h3>
      <div class="bp-month-nav">
        <button class="bp-nav-btn" @click="prevMonth" aria-label="Mes anterior">‹</button>
        <span class="bp-month-label">{{ monthLabel }}</span>
        <button class="bp-nav-btn" @click="nextMonth" aria-label="Mes siguiente">›</button>
      </div>
    </div>

    <div v-if="loading" class="bp-loading">
      <SkeletonLoader variant="card" width="100%" height="120px" />
      <SkeletonLoader variant="card" width="100%" height="120px" />
    </div>

    <div v-else-if="error" class="bp-error">
      <span>{{ error }}</span>
      <button class="btn btn-sm" @click="loadBudgets">Reintentar</button>
    </div>

    <template v-else>
      <div v-if="!budgetItems.length" class="bp-empty">
        <p>Aún no hay presupuestos configurados</p>
        <router-link to="/config" class="btn btn-primary">Configurar presupuestos</router-link>
      </div>

      <div v-else class="bp-content">
        <div class="bp-totals">
          <div class="bp-total-card">
            <span class="bp-total-label">Planificado</span>
            <span class="bp-total-value">${{ fmt(budgetTotals.planificado) }}</span>
          </div>
          <div class="bp-total-card">
            <span class="bp-total-label">Ejecutado <span class="bp-helper">(gastado hasta ahora)</span></span>
            <span class="bp-total-value expense">${{ fmt(budgetTotals.ejecutado) }}</span>
          </div>
          <div class="bp-total-card">
            <span class="bp-total-label">Disponible</span>
            <span class="bp-total-value">${{ fmt(budgetTotals.disponible) }}</span>
          </div>
          <div class="bp-total-card">
            <span class="bp-total-label">Proyectado al cierre</span>
            <span class="bp-total-value" :class="budgetProjection?.total_will_exceed ? 'expense' : ''">${{ fmt(budgetTotals.proyectado) }}</span>
          </div>
        </div>

        <div v-if="budgetAlertMessage" class="bp-alert">
          <AlertTriangle :size="16" /> {{ budgetAlertMessage }}
        </div>

        <div class="bp-category-grid">
          <div v-for="item in budgetItems" :key="item.category_id" class="bp-category-card">
            <div class="bp-cat-header">
              <span class="bp-cat-name">{{ item.category }}</span>
              <StatusBadge :label="statusLabel(item.status)" :variant="statusVariant(item.status)" />
            </div>
            <div class="bp-cat-bars">
              <div class="bp-bar-row">
                <span class="bp-bar-label">Planificado</span>
                <div class="bp-bar-track"><div class="bp-bar-fill bg-blue" :style="{ width: barWidth(item.budgeted, item.budgeted) }" /></div>
                <span class="bp-bar-amount">${{ fmt(item.budgeted) }}</span>
              </div>
              <div class="bp-bar-row">
                <span class="bp-bar-label">Ejecutado</span>
                <div class="bp-bar-track"><div class="bp-bar-fill" :class="fillVariant(item.status)" :style="{ width: barWidth(item.spent, item.budgeted) }" /></div>
                <span class="bp-bar-amount">${{ fmt(item.spent) }}</span>
              </div>
            </div>
            <div class="bp-cat-footer">
              <span class="bp-available">Disponible: ${{ fmt(item.budgeted - item.spent) }}</span>
              <span v-if="item.will_exceed" class="bp-projection over">Proyección: ${{ fmt(item.projected_spent) }} (+${{ fmt(item.projected_overrun) }})</span>
              <span v-else class="bp-projection">Proyección: ${{ fmt(item.projected_spent) }}</span>
            </div>
          </div>
        </div>

        <div class="bp-footer">
          <button class="btn btn-primary" @click="$emit('open-detail')">Ver detalle</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { AlertTriangle, BarChart3 } from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { useBudgets } from '@/composables/useBudgets'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()
const {
  loading, error, month, year, monthLabel, budgetItems, budgetTotals,
  budgetProjection, budgetAlertMessage, statusLabel,
  prevMonth, nextMonth, loadBudgets, loadCategories,
} = useBudgets()

onMounted(async () => {
  await loadCategories()
  await loadBudgets()
})

function barWidth(value, max) {
  const v = Number(value) || 0
  const m = Number(max) || 1
  return Math.min((v / m) * 100, 100) + '%'
}

function statusVariant(status) {
  const map = { ok: 'success', warning: 'warning', over: 'error' }
  return map[status] || 'default'
}

function fillVariant(status) {
  const map = { ok: 'bg-green', warning: 'bg-yellow', over: 'bg-red' }
  return map[status] || 'bg-blue'
}

defineEmits(['open-detail'])
</script>

<style scoped>
.budget-panel { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bp-header { display: flex; justify-content: space-between; align-items: center; }
.bp-title { font-family: var(--font-display); font-size: 1rem; font-weight: 600; margin: 0; }
.title-icon { margin-right: 4px; }
.bp-month-nav { display: flex; align-items: center; gap: 8px; }
.bp-nav-btn { background: none; border: none; font-size: 1.4rem; cursor: pointer; padding: 8px 12px; border-radius: var(--radius-sm); color: var(--color-neutral-600); min-width: 44px; min-height: 44px; display: inline-flex; align-items: center; justify-content: center; transition: background var(--transition-fast), transform var(--transition-fast); }
.bp-nav-btn:hover { background: var(--color-neutral-100); }
.bp-nav-btn:active { transform: scale(0.94); }
.bp-month-label { font-size: var(--font-size-sm-alt); font-weight: 500; color: var(--color-neutral-700); min-width: 100px; text-align: center; }

.bp-loading, .bp-error, .bp-empty { text-align: center; padding: var(--spacing-lg); color: var(--color-neutral-500); }
.bp-error { display: flex; flex-direction: column; align-items: center; gap: var(--spacing-sm); }

.bp-totals { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-sm); }
.bp-total-card { background: var(--color-neutral-0); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-md); padding: var(--spacing-md); display: flex; flex-direction: column; gap: 4px; }
.bp-total-label { font-size: var(--font-size-xs); color: var(--color-neutral-500); }
.bp-helper { font-size: var(--font-size-3xs); color: var(--color-neutral-400); font-weight: 400; }
.bp-total-value { font-family: var(--font-mono); font-size: 1rem; font-weight: 600; color: var(--color-neutral-900); }
.bp-total-value.expense { color: var(--color-error-600); }

.bp-alert { background: var(--color-warning-50); color: var(--color-warning-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: var(--font-size-sm-alt); }

.bp-category-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-sm); }
.bp-category-card { background: var(--color-neutral-0); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-md); padding: var(--spacing-md); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.bp-cat-header { display: flex; justify-content: space-between; align-items: center; }
.bp-cat-name { font-size: var(--font-size-sm-alt); font-weight: 500; color: var(--color-neutral-700); }
.bp-bar-row { display: flex; align-items: center; gap: var(--spacing-xs); }
.bp-bar-label { font-size: var(--font-size-2xs); color: var(--color-neutral-500); width: 60px; }
.bp-bar-track { flex: 1; height: 8px; background: var(--color-neutral-100); border-radius: 4px; overflow: hidden; }
.bp-bar-fill { height: 100%; border-radius: 4px; transition: width 300ms ease; }
.bp-bar-fill.bg-blue { background: var(--color-primary-500); }
.bp-bar-fill.bg-green { background: var(--color-success-500); }
.bp-bar-fill.bg-yellow { background: var(--color-warning-500); }
.bp-bar-fill.bg-red { background: var(--color-error-500); }
.bp-bar-amount { font-family: var(--font-mono); font-size: var(--font-size-xs); font-weight: 600; width: 70px; text-align: right; }
.bp-cat-footer { display: flex; justify-content: space-between; align-items: center; font-size: var(--font-size-xs); color: var(--color-neutral-500); }
.bp-available { font-weight: 500; }
.bp-projection { font-family: var(--font-mono); font-weight: 600; color: var(--color-neutral-700); }
.bp-projection.over { color: var(--color-error-600); }

.bp-footer { display: flex; justify-content: flex-end; padding-top: var(--spacing-sm); }

.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: var(--font-size-sm-alt); font-weight: 600; border: none; cursor: pointer; transition: transform var(--transition-fast); }
.btn:active:not(:disabled) { transform: scale(0.97); }
.btn-sm { font-size: var(--font-size-xs-alt); padding: var(--spacing-xs) var(--spacing-md); background: var(--color-neutral-100); color: var(--color-neutral-700); transition: transform var(--transition-fast); }
.btn-sm:active:not(:disabled) { transform: scale(0.96); }
.btn-primary { background: var(--color-primary-600); color: var(--color-neutral-0); }
.btn-primary:hover { background: var(--color-primary-700); }
.btn-primary:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }

@media (max-width: 768px) {
  .bp-totals { grid-template-columns: repeat(2, 1fr); }
  .bp-category-grid { grid-template-columns: 1fr; }
}
</style>
<template>
  <Teleport to="body">
    <div v-if="open" class="bdm-backdrop" @click.self="close">
      <FocusTrap :visible="open">
        <div class="bdm-modal" role="dialog" aria-modal="true" :aria-label="`Presupuesto detallado ${monthLabel}`">
          <div class="bdm-header">
            <h3 class="bdm-title">Presupuesto detallado — {{ monthLabel }}</h3>
            <button class="bdm-close" @click="close" aria-label="Cerrar"><X :size="18" /></button>
          </div>

          <div v-if="loading" class="bdm-body">
            <SkeletonLoader variant="card" width="100%" height="200px" />
          </div>

          <div v-else class="bdm-body">
            <div v-if="budgetAlertMessage" class="bdm-alert">
              <AlertTriangle :size="16" /> {{ budgetAlertMessage }}
            </div>

            <div class="bdm-chart">
              <Bar :data="chartData" :options="chartOptions" v-if="chartData" />
            </div>

            <div class="bdm-table-wrap">
              <table class="bdm-table">
                <thead>
                  <tr>
                    <th>Categoría</th>
                    <th>Planificado</th>
                    <th>Ejecutado</th>
                    <th>Disponible</th>
                    <th>% Ejecutado</th>
                    <th>Proyección</th>
                    <th>Estado</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in budgetItems" :key="item.category_id">
                    <td>{{ item.category }}</td>
                    <td>${{ fmt(item.budgeted) }}</td>
                    <td>${{ fmt(item.spent) }}</td>
                    <td>${{ fmt(item.budgeted - item.spent) }}</td>
                    <td>{{ pct(item) }}%</td>
                    <td>${{ fmt(item.projected_spent) }}</td>
                    <td><StatusBadge :label="statusLabel(item.status)" :variant="statusVariant(item.status)" /></td>
                    <td>
                      <button class="bdm-action" @click="$emit('edit', item)">Editar</button>
                      <button class="bdm-action danger" @click="$emit('delete', item)">Eliminar</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="bdm-footer">
              <button class="btn" @click="close">Cerrar</button>
              <router-link to="/config?tab=categories" class="btn btn-primary" @click="close">Configurar presupuestos</router-link>
            </div>
          </div>
        </div>
      </FocusTrap>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, watch, onMounted, onUnmounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { AlertTriangle, X } from 'lucide-vue-next'
import FocusTrap from '@/components/FocusTrap.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { useBudgets } from '@/composables/useBudgets'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close', 'edit', 'delete'])

const { fmt } = useCurrency()
const {
  loading, error, month, year, monthLabel, budgetItems, chartData, chartOptions,
  budgetAlertMessage, statusLabel, loadBudgets,
} = useBudgets()

watch(() => props.open, (val) => {
  if (val) loadBudgets()
})

function close() { emit('close') }

function onKeydown(e) {
  if (e.key === 'Escape' && props.open) close()
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

function pct(item) {
  const budgeted = Number(item.budgeted) || 1
  const spent = Number(item.spent) || 0
  return Math.min(((spent / budgeted) * 100), 100).toFixed(1)
}

function statusVariant(status) {
  const map = { ok: 'success', warning: 'warning', over: 'error' }
  return map[status] || 'default'
}
</script>

<style scoped>
.bdm-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: var(--spacing-md); }
.bdm-modal { background: var(--color-neutral-0); border-radius: var(--radius-lg); width: 100%; max-width: 900px; max-height: 90vh; display: flex; flex-direction: column; box-shadow: var(--shadow-lg); }
.bdm-header { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-lg); border-bottom: 1px solid var(--color-neutral-100); }
.bdm-title { font-family: var(--font-display); font-size: 1.1rem; font-weight: 600; margin: 0; }
.bdm-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 8px 12px; color: var(--color-neutral-500); min-width: 44px; min-height: 44px; display: inline-flex; align-items: center; justify-content: center; border-radius: var(--radius-sm); transition: transform var(--transition-fast); }
.bdm-close:hover { color: var(--color-neutral-900); background: var(--color-neutral-100); }
.bdm-close:active { transform: scale(0.94); }
.bdm-body { padding: var(--spacing-lg); overflow-y: auto; display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-alert { background: var(--color-warning-50); color: var(--color-warning-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: 0.85rem; }
.bdm-chart { height: 220px; }
.bdm-table-wrap { overflow-x: auto; }
.bdm-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.bdm-table th, .bdm-table td { padding: 10px 8px; text-align: left; border-bottom: 1px solid var(--color-neutral-100); }
.bdm-table th { font-weight: 600; color: var(--color-neutral-500); font-size: 0.75rem; text-transform: uppercase; }
.bdm-action { background: none; border: none; color: var(--color-primary-600); cursor: pointer; font-size: 0.8rem; font-weight: 500; transition: opacity var(--transition-fast); }
.bdm-action.danger { color: var(--color-error-600); }
.bdm-action:active { opacity: 0.7; }
.bdm-footer { display: flex; justify-content: space-between; padding-top: var(--spacing-md); border-top: 1px solid var(--color-neutral-100); }
.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; transition: transform var(--transition-fast); }
.btn:active:not(:disabled) { transform: scale(0.97); }
.btn-primary { background: var(--color-primary-600); color: var(--color-neutral-0); transition: transform var(--transition-fast); }
.btn-primary:hover { background: var(--color-primary-700); }
.btn-primary:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }
</style>
<template>
  <div class="bdm-categories">
    <div v-if="grouped" class="bdm-cats-banner" data-testid="cats-banner" role="status">
      <strong>¡Listo!</strong> Distribuimos tu ingreso. Ahora asignemos las categorías.
    </div>

    <!-- GROUPED VIEW (create flow) -->
    <template v-if="grouped && groups.length">
      <div class="bdm-groups">
        <section
          v-for="g in groupsWithItems"
          :key="g.key"
          class="bdm-group-section"
          :data-group-key="g.key"
        >
          <header class="bdm-group-section-head">
            <div class="bdm-group-section-titles">
              <h4 class="bdm-group-section-name">{{ g.label }}</h4>
              <span class="bdm-group-available">${{ fmt(groupAmounts[g.key] || 0) }} disponibles</span>
            </div>
            <span class="bdm-group-section-pct">{{ g.pct }}%</span>
          </header>
          <div class="bdm-group-section-bar" aria-hidden="true">
            <div class="bdm-group-section-fill" :style="{ width: g.pct + '%' }" />
          </div>

          <div
            v-for="item in g.items"
            :key="item.category_id"
            class="bdm-group-item"
            data-testid="group-category-row"
          >
            <div class="bdm-group-item-left">
              <span class="bdm-group-item-name">{{ item.category }}</span>
              <span class="bdm-group-item-tag">{{ g.label }}</span>
            </div>
            <span class="bdm-group-item-amount">${{ fmt(item.budgeted) }}</span>
          </div>

          <p v-if="g.items.length === 0" class="bdm-group-empty">Sin categorías asignadas a este grupo.</p>
        </section>

        <section v-if="unassignedItems.length" class="bdm-group-section bdm-group-section--unassigned">
          <header class="bdm-group-section-head">
            <div class="bdm-group-section-titles">
              <h4 class="bdm-group-section-name">Sin asignar</h4>
              <span class="bdm-group-available">Elige un grupo para cada categoría</span>
            </div>
          </header>
          <div
            v-for="item in unassignedItems"
            :key="item.category_id"
            class="bdm-group-item"
            data-testid="group-category-row"
          >
            <div class="bdm-group-item-left">
              <span class="bdm-group-item-name">{{ item.category }}</span>
              <span class="bdm-group-item-tag bdm-group-item-tag--none">Sin grupo</span>
            </div>
            <div class="bdm-group-item-right">
              <span class="bdm-group-item-amount">${{ fmt(item.budgeted) }}</span>
              <select
                class="bdm-group-select"
                :aria-label="`Grupo para ${item.category}`"
                :value="categoryGroups[item.category_id] || ''"
                @change="assignGroup(item.category_id, $event.target.value)"
              >
                <option value="" disabled>Asignar grupo</option>
                <option v-for="g in groups" :key="g.key" :value="g.key">{{ g.label }}</option>
              </select>
            </div>
          </div>
        </section>
      </div>
    </template>

    <!-- FLAT TABLE (view mode / fallback) -->
    <template v-else>
      <div class="bdm-chart">
        <Bar :data="chartData" :options="chartOptions" v-if="chartData" />
      </div>

      <div class="bdm-table-wrap">
        <table class="bdm-table">
          <thead>
            <tr>
              <th>Categoría</th>
              <th>Grupo</th>
              <th>Planificado</th>
              <th>Ejecutado</th>
              <th>Disponible</th>
              <th>% Ejecutado</th>
              <th>Proyección</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.category_id">
              <td>
                <span class="bdm-cat-name">{{ item.category }}</span>
                <span class="bdm-cat-group" data-testid="category-group">{{ groupOf(item.category_id) }}</span>
              </td>
              <td>
                <template v-if="editingGroupFor === item.category_id">
                  <select
                    v-model="pendingGroup"
                    class="bdm-group-select"
                    :aria-label="`Grupo para ${item.category}`"
                  >
                    <option v-for="g in groups" :key="g.key" :value="g.key">{{ g.label }}</option>
                  </select>
                  <div class="bdm-group-btns">
                    <button class="bdm-link" @click="saveGroup">Guardar</button>
                    <button class="bdm-link" @click="cancelGroup">Cancelar</button>
                  </div>
                </template>
                <template v-else>
                  <button v-if="groups.length" class="bdm-link" @click="startEdit(item)">Cambiar grupo</button>
                </template>
              </td>
              <td>${{ fmt(item.budgeted) }}</td>
              <td>${{ fmt(item.spent) }}</td>
              <td>${{ fmt(item.budgeted - item.spent) }}</td>
              <td>{{ pct(item) }}%</td>
              <td>${{ fmt(item.projected_spent) }}</td>
              <td><StatusBadge :label="statusLabel(item.status)" :variant="statusVariant(item.status)" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div class="bdm-continue-wrap">
      <button class="bdm-continue-btn btn btn-primary" data-testid="continue-btn" @click="$emit('continue')">Continuar →</button>
    </div>

    <p v-if="groupMsg" class="bdm-ok" role="status">{{ groupMsg }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import StatusBadge from '@/components/StatusBadge.vue'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({
  items: { type: Array, required: true },
  chartData: { type: Object, default: null },
  chartOptions: { type: Object, default: () => ({}) },
  groups: { type: Array, default: () => [] },
  categoryGroups: { type: Object, default: () => ({}) },
  grouped: { type: Boolean, default: false },
  groupAmounts: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['save-group', 'continue'])
const { fmt } = useCurrency()

const editingGroupFor = ref(null)
const pendingGroup = ref('')
const groupMsg = ref('')

function groupOf(categoryId) {
  const key = props.categoryGroups[categoryId]
  if (!key) return 'Sin asignar'
  const group = props.groups.find(g => g.key === key)
  return group ? group.label : key
}

const groupsWithItems = computed(() => {
  return props.groups.map((g) => ({
    ...g,
    items: props.items.filter((item) => props.categoryGroups[item.category_id] === g.key),
  }))
})

const unassignedItems = computed(() =>
  props.items.filter((item) => !props.categoryGroups[item.category_id])
)

function assignGroup(categoryId, groupKey) {
  if (!groupKey) return
  emit('save-group', { categoryId, groupKey })
  groupMsg.value = 'Grupo actualizado.'
}

function startEdit(item) {
  editingGroupFor.value = item.category_id
  pendingGroup.value = props.categoryGroups[item.category_id] || ''
  groupMsg.value = ''
}

function cancelGroup() {
  editingGroupFor.value = null
  pendingGroup.value = ''
}

function saveGroup() {
  if (!pendingGroup.value || !editingGroupFor.value) return
  emit('save-group', { categoryId: editingGroupFor.value, groupKey: pendingGroup.value })
  editingGroupFor.value = null
  groupMsg.value = 'Grupo actualizado.'
}

function pct(item) {
  const budgeted = Number(item.budgeted) || 1
  const spent = Number(item.spent) || 0
  return Math.min((spent / budgeted) * 100, 100).toFixed(1)
}

function statusVariant(status) {
  const map = { ok: 'success', warning: 'warning', over: 'error' }
  return map[status] || 'default'
}

function statusLabel(status) {
  const map = { ok: 'Vamos bien', warning: 'Cuidado', over: 'Nos pasamos' }
  return map[status] || status
}
</script>

<style scoped>
.bdm-categories { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-cats-banner { background: var(--color-success-50); color: var(--color-success-700); border: 1px solid var(--color-success-500); border-radius: var(--radius-md); padding: var(--spacing-sm) var(--spacing-md); font-size: 0.9rem; }
.bdm-cats-banner strong { font-weight: 700; }
.bdm-groups { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-group-section { background: var(--color-neutral-0); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-md); padding: var(--spacing-md); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.bdm-group-section--unassigned { border-style: dashed; background: var(--color-neutral-50); }
.bdm-group-section-head { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--spacing-sm); }
.bdm-group-section-titles { display: flex; flex-direction: column; gap: 2px; }
.bdm-group-section-name { font-size: 0.95rem; font-weight: 700; color: var(--color-neutral-900); margin: 0; }
.bdm-group-available { font-size: 0.8rem; color: var(--color-neutral-500); font-family: var(--font-mono); }
.bdm-group-section-pct { font-family: var(--font-mono); font-size: 0.8rem; font-weight: 700; color: var(--color-primary-700); background: var(--color-primary-100); padding: 2px 8px; border-radius: 999px; }
.bdm-group-section-bar { height: 8px; background: var(--color-neutral-100); border-radius: 4px; overflow: hidden; }
.bdm-group-section-fill { height: 100%; background: var(--color-primary-500); border-radius: 4px; transition: width var(--transition-slow); }
.bdm-group-item { display: flex; justify-content: space-between; align-items: center; gap: var(--spacing-md); padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-50); }
.bdm-group-item:last-child { border-bottom: none; }
.bdm-group-item-left { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.bdm-group-item-name { font-size: 0.9rem; font-weight: 500; color: var(--color-neutral-900); }
.bdm-group-item-tag { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-neutral-500); }
.bdm-group-item-tag--none { color: var(--color-warning-700); }
.bdm-group-item-amount { font-family: var(--font-mono); font-size: 0.95rem; font-weight: 700; color: var(--color-neutral-900); white-space: nowrap; }
.bdm-group-item-right { display: flex; align-items: center; gap: var(--spacing-sm); }
.bdm-group-empty { font-size: 0.8rem; color: var(--color-neutral-400); margin: 0; font-style: italic; }
.bdm-chart { height: 220px; }
.bdm-table-wrap { overflow-x: auto; }
.bdm-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.bdm-table th, .bdm-table td { padding: 10px 8px; text-align: left; border-bottom: 1px solid var(--color-neutral-100); }
.bdm-table th { font-weight: 600; color: var(--color-neutral-500); font-size: 0.75rem; text-transform: uppercase; }
.bdm-cat-name { display: block; font-weight: 500; color: var(--color-neutral-900); }
.bdm-cat-group { display: block; font-size: 0.8rem; color: var(--color-neutral-500); margin-top: 2px; }
.bdm-group-select { padding: var(--spacing-xs) var(--spacing-sm); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); font-size: 0.85rem; background: var(--color-neutral-0); color: var(--color-neutral-800); min-height: 44px; }
.bdm-group-btns { display: flex; gap: var(--spacing-sm); margin-top: 4px; }
.bdm-link { background: none; border: none; color: var(--color-primary-600); cursor: pointer; font-size: 0.85rem; font-weight: 500; padding: var(--spacing-sm) var(--spacing-xs); min-height: 44px; display: inline-flex; align-items: center; }
.bdm-link:hover { text-decoration: underline; }
.bdm-ok { background: var(--color-success-50); color: var(--color-success-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: 0.85rem; margin: 0; }
.bdm-continue-wrap { display: flex; justify-content: flex-end; padding-top: var(--spacing-md); }
.bdm-continue-btn { min-height: 48px; padding: var(--spacing-sm) var(--spacing-lg); }
@media (prefers-reduced-motion: reduce) { .bdm-group-section-fill { transition: none; } }
</style>

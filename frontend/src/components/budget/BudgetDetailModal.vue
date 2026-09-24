<template>
  <Teleport to="body">
    <div v-if="open" class="bdm-backdrop" @click.self="close">
      <FocusTrap :visible="open">
        <div class="bdm-modal" role="dialog" aria-modal="true" :aria-label="modalTitle">
          <div class="bdm-header">
            <h3 class="bdm-title">{{ modalTitle }}</h3>
            <button class="bdm-close" @click="close" aria-label="Cerrar"><X :size="18" /></button>
          </div>

          <!-- Wizard progress (create only) -->
          <div
            v-if="currentMode === 'create' && wizardStep"
            class="bdm-wizard"
            data-testid="wizard-progress"
            role="progressbar"
            :aria-valuenow="wizardPct"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`Progreso: paso ${wizardMeta.n} de 4, ${wizardMeta.label}`"
          >
            <div class="bdm-wizard-label">
              <span>Paso {{ wizardMeta.n }} de 4 · {{ wizardMeta.label }}</span>
              <span class="bdm-wizard-pct">{{ wizardPct }}%</span>
            </div>
            <div class="bdm-wizard-track">
              <div class="bdm-wizard-fill" :style="{ width: wizardPct + '%' }" />
            </div>
          </div>

          <!-- Tabs: view only (hidden during create wizard and edit) -->
          <div v-if="currentMode === 'view'" ref="tabsRef" class="bdm-tabs" role="tablist" aria-label="Secciones del presupuesto">
            <button
              v-for="(tab, idx) in tabs"
              :key="tab.id"
              role="tab"
              :id="`bdm-tab-${tab.id}`"
              :aria-selected="activeTab === tab.id"
              :tabindex="activeTab === tab.id ? 0 : -1"
              class="bdm-tab"
              :class="{ active: activeTab === tab.id }"
              @click="selectTab(tab.id)"
              @keydown="onTabKeydown($event, idx)"
            >{{ tab.label }}</button>
          </div>

          <div v-if="loading" class="bdm-body">
            <SkeletonLoader variant="card" width="100%" height="200px" />
          </div>

          <!-- CREATE MODE — Progressive onboarding -->
          <div v-else-if="currentMode === 'create'" class="bdm-body">
            <!-- HERO -->
            <template v-if="creationStep === 'method'">
              <div class="bdm-hero">
                <h3 class="bdm-hero-title">Configuremos tu presupuesto de {{ monthLabelShort }}</h3>
                <p class="bdm-hero-sub">En menos de un minuto tendrás una distribución lista.</p>
              </div>

              <div class="bdm-onboarding-options">
                <button
                  class="bdm-onboarding-option bdm-onboarding-option--primary"
                  data-testid="onboard-method"
                  @click="goToMethodCatalog"
                >
                  <span class="bdm-onboarding-option-icon">📊</span>
                  <span class="bdm-onboarding-option-title">Usar un método</span>
                  <span class="bdm-onboarding-option-desc">50/30/20, 70/20/10 y más.</span>
                  <span class="bdm-onboarding-option-badge">Recomendada</span>
                </button>

                <button
                  class="bdm-onboarding-option"
                  data-testid="onboard-manual"
                  @click="startManualCreation"
                >
                  <span class="bdm-onboarding-option-icon">✏️</span>
                  <span class="bdm-onboarding-option-title">Ingresar montos manualmente</span>
                  <span class="bdm-onboarding-option-desc">Configurar todo desde cero.</span>
                </button>
              </div>

              <p v-if="savedMethodName" class="bdm-hero-note" data-testid="hero-previous-hint">
                Ya usaste {{ savedMethodName }} antes. Podrás reutilizar esa configuración después de elegir un método.
              </p>
              <p class="bdm-hero-footnote">Puedes cambiar de método después.</p>
            </template>

            <!-- METHOD / CATEGORIES (post-hero) -->
            <template v-else-if="creationStep === 'method-choose'">
              <Transition name="bdm-tab" mode="out-in">
                <div
                  :key="activeTab"
                  role="tabpanel"
                  class="bdm-panel"
                >
                  <template v-if="activeTab === 'metodo'">
                    <BudgetMethodTab
                      ref="methodTabRef"
                      :current-method="savedMethodName"
                      :creation-step="creationStep"
                      :suppress-current-hint="true"
                      @apply="handleApplyMethod"
                    />
                  </template>

                  <template v-else-if="activeTab === 'categorias'">
                    <BudgetCategoriesTab
                      :items="categoryDisplayItems"
                      :chart-data="categoryChartData"
                      :chart-options="chartOptions"
                      :groups="configGroups"
                      :category-groups="groupMapping"
                      :grouped="true"
                      :group-amounts="groupAmounts"
                      @save-group="saveGroupChange"
                      @continue="handleCategoriesContinue"
                    />
                  </template>
                </div>
              </Transition>

              <p v-if="applyMsg" class="bdm-apply-ok" role="status" data-testid="apply-msg">{{ applyMsg }}</p>

              <div class="bdm-row-btns bdm-onboarding-nav">
                <button
                  v-if="activeTab === 'categorias'"
                  class="btn"
                  data-testid="back-to-options"
                  @click="activeTab = 'metodo'"
                >
                  Volver al método
                </button>
              </div>
            </template>

            <!-- SUMMARY -->
            <template v-else-if="creationStep === 'summary'">
              <p v-if="formError" class="bdm-error" role="alert" aria-live="assertive">{{ formError }}</p>

              <div class="bdm-summary-section">
                <h3 class="bdm-summary-h3">Revisa tu presupuesto</h3>

                <div class="bdm-summary-grid">
                  <div class="bdm-summary-card">
                    <p class="bdm-summary-label">Método elegido</p>
                    <p class="bdm-summary-value">{{ savedMethodName || 'Personalizado' }}</p>
                  </div>
                  <div class="bdm-summary-card">
                    <p class="bdm-summary-label">Distribución</p>
                    <p class="bdm-summary-value">{{ formatDistribution }}</p>
                  </div>
                  <div class="bdm-summary-card">
                    <p class="bdm-summary-label">Categorías asignadas</p>
                    <p class="bdm-summary-value">{{ groupMappingCount }} de {{ categories.length }}</p>
                  </div>
                  <div class="bdm-summary-card">
                    <p class="bdm-summary-label">Ingreso de referencia</p>
                    <p class="bdm-summary-value">${{ incomeAmount || '—' }}</p>
                  </div>
                </div>

                <div class="bdm-summary-budgets">
                  <p class="bdm-summary-label">Desglose por categorías</p>
                  <ul data-testid="summary-budget-list">
                    <li v-for="row in summaryBudgetRows" :key="row.id">
                      <span>{{ row.name }}</span>
                      <strong>{{ fmt(row.amount) }}</strong>
                    </li>
                  </ul>
                </div>

                <div v-if="methodSaving" class="bdm-apply-ok" role="status">
                  Método guardado. Tus presupuestos existentes no cambiaron.
                </div>
              </div>

              <div class="bdm-row-btns bdm-onboarding-nav">
                <button class="btn" data-testid="summary-back" @click="backFromSummary">Volver</button>
                <button class="btn btn-primary" data-testid="create-budget-btn" @click="handleSaveCreate" :disabled="saving">{{ saving ? 'Creando...' : 'Crear presupuesto' }}</button>
              </div>
            </template>

            <!-- MANUAL CREATION (bypass) -->
            <template v-if="creationStep === 'manual'">
              <p class="bdm-hint">Asigna un monto a cada categoría de gasto para tu presupuesto mensual.</p>
              <div v-if="formError" class="bdm-error" role="alert" aria-live="assertive">{{ formError }}</div>
              <div v-if="categories.length === 0" class="bdm-empty"><p>No hay categorías de gasto disponibles.</p></div>
              <div v-else class="bdm-form-list">
                <div v-for="cat in categories" :key="cat.id" class="bdm-form-row">
                  <label class="bdm-form-label" :for="`create-${cat.id}`">{{ cat.name }}</label>
                  <div class="bdm-form-input-wrap">
                    <span class="bdm-form-prefix">$</span>
                    <input :id="`create-${cat.id}`" type="number" class="bdm-form-input" :value="getFormAmount(cat.id)" @input="setFormAmount(cat.id, $event.target.value)" min="0" step="1000" placeholder="0" aria-describedby="create-help" />
                  </div>
                </div>
                <p id="create-help" class="bdm-form-help">Opcional. Puedes dejar en 0 las categorías que no apliquen.</p>
              </div>
              <div class="bdm-row-btns bdm-onboarding-nav">
                <button class="btn" data-testid="manual-back" @click="backToHero">Volver</button>
              </div>
            </template>
          </div>

          <!-- VIEW MODE — Budget Hub panels -->
          <div v-else-if="currentMode === 'view'" class="bdm-body">
            <div v-if="showOnboarding" class="bdm-onboard" aria-label="Progreso de configuración">
              <p class="bdm-onboard-title">Configurar tu presupuesto</p>
              <ol class="bdm-onboard-steps">
                <li v-for="step in onboardingSteps" :key="step.id" class="bdm-onboard-step" :class="{ done: step.done, current: step.id === currentStepId }" :aria-current="step.id === currentStepId ? 'step' : undefined">
                  <span class="bdm-onboard-dot" aria-hidden="true">{{ step.done ? '✓' : (step.id === currentStepId ? '●' : '○') }}</span>
                  {{ step.label }}
                </li>
              </ol>
            </div>

            <Transition name="bdm-tab" mode="out-in">
              <div :key="activeTab" role="tabpanel" :id="`bdm-panel-${activeTab}`" :aria-labelledby="`bdm-tab-${activeTab}`" class="bdm-panel">
                <template v-if="activeTab === 'resumen'">
                  <div v-if="budgetAlertMessage" class="bdm-alert"><AlertTriangle :size="16" aria-hidden="true" /> {{ budgetAlertMessage }}</div>
                  <div class="bdm-kpis">
                    <div class="bdm-kpi-row"><span class="bdm-kpi-label">Gastado</span><strong class="bdm-kpi-value">${{ fmt(totals.ejecutado) }} <span class="bdm-kpi-muted">de ${{ fmt(totals.planificado) }}</span></strong></div>
                    <div class="bdm-progress-track" role="progressbar" :aria-valuenow="progressPct" aria-valuemin="0" aria-valuemax="100" :aria-label="`Progreso del presupuesto: ${progressPct}%`"><div class="bdm-progress-fill" :style="{ width: progressPct + '%' }" /></div>
                    <div class="bdm-kpi-row"><span class="bdm-kpi-label">Disponible</span><strong class="bdm-kpi-value">${{ fmt(totals.disponible) }}</strong></div>
                    <div class="bdm-status-row"><StatusBadge :label="overallStatus.label" :variant="overallStatus.variant" /><span class="bdm-status-text">{{ overallStatus.message }}</span></div>
                  </div>
                </template>
                <template v-else-if="activeTab === 'categorias'">
                  <BudgetCategoriesTab :items="budgetItems" :chart-data="chartData" :chart-options="chartOptions" :groups="configGroups" :category-groups="groupMapping" @save-group="saveGroupChange" @continue="handleCategoriesContinue" />
                </template>
                <template v-else-if="activeTab === 'metodo'">
                  <BudgetMethodTab ref="methodTabRef" :current-method="savedMethodName" @apply="handleApplyMethod" />
                </template>
                <template v-else>
                  <BudgetConfigurationTab ref="configTabRef" :month-label="monthLabel" :status="overallStatus" :last-updated="lastUpdatedText" :saving="methodSaving" @save="handleConfigSave" />
                </template>
              </div>
            </Transition>
          </div>

          <!-- EDIT MODE -->
          <div v-else-if="currentMode === 'edit'" class="bdm-body">
            <p class="bdm-hint">Edita los montos de tu presupuesto. Los cambios se guardarán al confirmar.</p>
            <div v-if="formError" class="bdm-error" role="alert" aria-live="assertive">{{ formError }}</div>
            <div v-if="budgetItems.length === 0" class="bdm-empty"><p>No hay presupuestos para editar.</p></div>
            <div v-else class="bdm-form-list">
              <div v-for="item in budgetItems" :key="item.category_id" class="bdm-form-row">
                <label class="bdm-form-label" :for="`edit-${item.category_id}`">{{ item.category }}</label>
                <div class="bdm-form-input-wrap">
                  <span class="bdm-form-prefix">$</span>
                  <input :id="`edit-${item.category_id}`" type="number" class="bdm-form-input" :value="getFormAmount(item.category_id)" @input="setFormAmount(item.category_id, $event.target.value)" min="0" step="1000" />
                </div>
              </div>
            </div>
          </div>

          <div class="bdm-footer">
            <!-- CREATE footer -->
            <template v-if="currentMode === 'create'">
              <template v-if="creationStep === 'method'">
                <button class="btn" @click="close">Cancelar</button>
              </template>
              <template v-else-if="creationStep === 'method-choose'">
                <button class="btn" @click="close">Cancelar</button>
                <button
                  v-if="activeTab === 'categorias'"
                  class="btn btn-primary"
                  data-testid="continue-footer-btn"
                  @click="handleCategoriesContinue"
                  :disabled="methodSaving"
                >
                  Continuar →
                </button>
              </template>
              <template v-else-if="creationStep === 'summary'">
                <button class="btn" data-testid="summary-back-footer" @click="backFromSummary">Volver</button>
                <button class="btn btn-primary" data-testid="create-budget-footer" @click="handleSaveCreate" :disabled="saving">{{ saving ? 'Creando...' : 'Crear presupuesto' }}</button>
              </template>
              <template v-else-if="creationStep === 'manual'">
                <button class="btn" @click="close">Cancelar</button>
                <button class="btn btn-primary" @click="handleSaveCreate" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar presupuesto' }}</button>
              </template>
            </template>
            <!-- VIEW footer -->
            <template v-else-if="currentMode === 'view'">
              <button class="btn" @click="close">Cerrar</button>
              <button class="btn btn-primary" @click="enterEdit">Editar presupuesto</button>
            </template>
            <!-- EDIT footer -->
            <template v-else>
              <button class="btn" @click="cancelEdit">Cancelar</button>
              <button class="btn btn-primary" @click="handleSaveEdit" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
            </template>
          </div>
        </div>
      </FocusTrap>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { AlertTriangle, X } from 'lucide-vue-next'
import FocusTrap from '@/components/FocusTrap.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import BudgetCategoriesTab from './BudgetCategoriesTab.vue'
import BudgetMethodTab from './BudgetMethodTab.vue'
import BudgetConfigurationTab from './BudgetConfigurationTab.vue'
import { useBudgets } from '@/composables/useBudgets'
import { useBudgetMethod } from '@/composables/useBudgetMethod'
import { useCurrency } from '@/composables/useCurrency'
import { useToast } from '@/composables/useToast'
import { listBudgetMethods } from '@/constants/budgetMethods'

const props = defineProps({
  open: Boolean,
  mode: {
    type: String,
    default: 'view',
    validator: (v) => ['create', 'view', 'edit'].includes(v),
  },
})

const emit = defineEmits(['close', 'saved'])

const { fmt } = useCurrency()
const toast = useToast()
const {
  loading, monthLabel, budgetItems, chartData, chartOptions,
  budgetAlertMessage, statusLabel, loadBudgets, budgetTotals,
  createBudget, editBudget, unbudgetedCategories, loadCategories,
} = useBudgets()
const {
  presets, presetsLoading, config,
  loadPresets, loadConfig, saveConfig, fetchPreview, resetPreview,
} = useBudgetMethod()

const currentMode = ref(props.mode)
const saving = ref(false)
const formBudgets = ref([])
const formError = ref('')
const activeTab = ref('resumen')
const tabsRef = ref(null)
const visitedResumen = ref(false)
const methodReady = ref(false)
const methodTabRef = ref(null)
const configTabRef = ref(null)

const creationStep = ref('method')

const tabs = [
  { id: 'resumen', label: 'Resumen' },
  { id: 'categorias', label: 'Categorías' },
  { id: 'metodo', label: 'Método' },
  { id: 'configuracion', label: 'Configuración' },
]

const groupMapping = ref({})
const incomeAmount = ref('')
const previewIncome = ref('')
const methodSaving = ref(false)
const activeMethodId = ref(null)
const applyMsg = ref('')

const configGroups = computed(() => (config.value && config.value.groups) || [])
const savedMethodName = computed(() => {
  const mt = config.value && config.value.method_type
  if (!mt) return ''
  const preset = (presets.value || []).find((p) => p.id === mt)
  return preset ? preset.name : 'Personalizado'
})

const groupMappingCount = computed(() => Object.keys(groupMapping.value || {}).length)

const monthLabelShort = computed(() => {
  const label = monthLabel.value || ''
  return label.split(' ')[0] || label
})

const formatDistribution = computed(() => {
  const method = listBudgetMethods().find(m => m.id === activeMethodId.value)
  if (!method) return ''
  return method.groups.map(g => `${g.pct}%`).join(' / ')
})

const totals = computed(() => budgetTotals.value ?? { planificado: 0, ejecutado: 0, disponible: 0, proyectado: 0 })
const progressPct = computed(() => {
  const planned = Number(totals.value.planificado) || 0
  if (planned === 0) return 0
  return Math.min(Math.round((Number(totals.value.ejecutado) / planned) * 100), 100)
})
const overallStatus = computed(() => {
  const items = budgetItems.value || []
  if (items.some((i) => i.status === 'over')) return { label: 'Nos pasamos', variant: 'error', message: 'Te pasaste del presupuesto este mes.' }
  if (items.some((i) => i.status === 'warning')) return { label: 'Cuidado', variant: 'warning', message: 'Vas cerca del límite en algunas categorías.' }
  return { label: 'Vamos bien', variant: 'success', message: 'Todo va dentro de lo planeado.' }
})

const methodPresets = listBudgetMethods()
const activeMethodPreset = computed(() => methodPresets.find(m => m.id === config.value?.method_type))

const WIZARD_META = {
  hero: { n: 1, label: 'Elegir cómo empezar' },
  method: { n: 2, label: 'Elegir método' },
  categories: { n: 3, label: 'Asignar categorías' },
  summary: { n: 4, label: 'Revisar resumen' },
}

const wizardStep = computed(() => {
  if (currentMode.value !== 'create') return null
  if (creationStep.value === 'method') return 'hero'
  if (creationStep.value === 'method-choose') {
    return activeTab.value === 'categorias' ? 'categories' : 'method'
  }
  if (creationStep.value === 'summary') return 'summary'
  return null
})

const wizardMeta = computed(() => WIZARD_META[wizardStep.value] || WIZARD_META.hero)
const wizardPct = computed(() => Math.round((wizardMeta.value.n / 4) * 100))

function selectTab(id) {
  activeTab.value = id
  if (id === 'resumen') visitedResumen.value = true
}

function onTabKeydown(e, idx) {
  const navKeys = ['ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp', 'Home', 'End']
  if (!navKeys.includes(e.key)) return
  e.preventDefault()
  const last = tabs.length - 1
  let next = idx
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = idx === last ? 0 : idx + 1
  else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = idx === 0 ? last : idx - 1
  else if (e.key === 'Home') next = 0
  else if (e.key === 'End') next = last
  selectTab(tabs[next].id)
  tabsRef.value?.querySelectorAll('[role="tab"]')[next]?.focus()
}

const onboardingSteps = computed(() => {
  const hasBudgets = (budgetItems.value || []).length > 0
  const mappingKeys = Object.keys(groupMapping.value || {}).length
  return [
    { id: 'crear', label: 'Crear presupuesto', done: hasBudgets },
    { id: 'metodo', label: 'Elegir método', done: !!(config.value && config.value.method_type) },
    { id: 'categorias', label: 'Asignar categorías', done: mappingKeys > 0 },
    { id: 'resumen', label: 'Revisar resumen', done: visitedResumen.value },
  ]
})

const currentStepId = computed(() => {
  const pending = onboardingSteps.value.find((s) => !s.done)
  return pending ? pending.id : null
})

const showOnboarding = computed(() => {
  return currentMode.value === 'view' && methodReady.value && currentStepId.value !== null
})

function configSnapshot() {
  const c = config.value || {}
  return {
    method_type: c.method_type ?? null,
    groups: c.groups ?? [],
    category_groups: { ...(c.category_groups ?? {}) },
    reference_income_source: c.reference_income_source ?? 'manual',
    reference_income_amount: c.reference_income_amount ?? null,
  }
}

function syncFromConfig() {
  groupMapping.value = { ...((config.value && config.value.category_groups) || {}) }
  const amt = config.value && config.value.reference_income_amount
  incomeAmount.value = amt === null || amt === undefined ? '' : String(amt)
}

async function handleConfigSave(payload) {
  methodSaving.value = true
  try {
    const result = await saveConfig({ ...configSnapshot(), reference_income_source: payload.source, reference_income_amount: payload.amount === '' ? null : String(payload.amount) })
    config.value = result
    syncFromConfig()
    emit('saved')
  } catch { /* handled by child component */ } finally { methodSaving.value = false }
}

async function saveGroupChange({ categoryId, groupKey }) {
  groupMapping.value = { ...groupMapping.value, [categoryId]: groupKey }
  try {
    const result = await saveConfig({ ...configSnapshot(), category_groups: groupMapping.value })
    config.value = result
    syncFromConfig()
    emit('saved')
  } catch { /* handled by child component */ }
}

function computeFormBudgetsFromMethod(groups, incomeRaw) {
  const income = Number(incomeRaw) || Number(config.value?.reference_income_amount) || 0
  const cats = categories.value
  if (!cats.length || !groups.length || income <= 0) {
    formBudgets.value = []
    return
  }
  const mapping = { ...groupMapping.value }
  const fallback = groups[0]?.key || ''
  for (const c of cats) {
    if (!mapping[c.id]) mapping[c.id] = fallback
  }
  groupMapping.value = mapping
  const byGroup = {}
  for (const c of cats) {
    const key = mapping[c.id]
    if (!byGroup[key]) byGroup[key] = []
    byGroup[key].push(c.id)
  }
  formBudgets.value = cats.map((c) => {
    const key = mapping[c.id]
    const g = groups.find((x) => x.key === key)
    const pct = g ? Number(g.pct) : 0
    const n = byGroup[key]?.length || 1
    const amount = Math.round((income * pct) / 100 / n)
    return { id: c.id, amount }
  })
}

async function handleApplyMethod({ methodId, groups, incomeAmount: incomeRaw }) {
  methodSaving.value = true
  activeMethodId.value = methodId
  try {
    const incomeToSave = incomeRaw !== undefined && incomeRaw !== '' ? String(incomeRaw) : (config.value?.reference_income_amount ?? null)
    const result = await saveConfig({
      ...configSnapshot(),
      method_type: methodId,
      groups,
      category_groups: groupMapping.value,
      reference_income_amount: incomeToSave,
    })
    config.value = result
    syncFromConfig()
    emit('saved')
    applyMsg.value = 'Método guardado. Tus presupuestos existentes no cambiaron.'
    if (currentMode.value === 'create') {
      const incomeForBudgets = incomeRaw || result?.reference_income_amount || config.value?.reference_income_amount
      computeFormBudgetsFromMethod(groups, incomeForBudgets)
      creationStep.value = 'method-choose'
      activeTab.value = 'categorias'
      toast.success('¡Listo!')
      window.$toast?.success?.('¡Listo!')
    }
  } catch { /* handled by child component */ } finally { methodSaving.value = false }
}

function handleCategoriesContinue() {
  if (currentMode.value === 'create') {
    if (!formBudgets.value.some((e) => Number(e.amount) > 0)) {
      formError.value = 'Aplica un método con ingreso de referencia o asigna montos antes de continuar.'
      activeTab.value = 'metodo'
      return
    }
    formError.value = ''
    creationStep.value = 'summary'
    activeTab.value = 'categorias'
  }
}

function goToMethodCatalog() {
  creationStep.value = 'method-choose'
  activeTab.value = 'metodo'
}

function backToHero() {
  creationStep.value = 'method'
  activeTab.value = 'metodo'
  formError.value = ''
}

function backFromSummary() {
  creationStep.value = 'method-choose'
  activeTab.value = 'categorias'
}

function startManualCreation() {
  creationStep.value = 'manual'
  initFormBudgets()
}

function resetMethodTab() {
  methodTabRef.value?.reset()
  configTabRef.value?.reset()
  incomeAmount.value = ''
  groupMapping.value = {}
}

const modalTitle = computed(() => {
  if (currentMode.value === 'create') return `Nuevo presupuesto — ${monthLabel.value}`
  if (currentMode.value === 'edit') return `Editar presupuesto — ${monthLabel.value}`
  return `Presupuesto detallado — ${monthLabel.value}`
})

const categories = computed(() => unbudgetedCategories.value)

const isCreateMethodFlow = computed(() => currentMode.value === 'create' && creationStep.value === 'method-choose')

const categoryDisplayItems = computed(() => {
  if (!isCreateMethodFlow.value || activeTab.value !== 'categorias') return budgetItems.value
  return categories.value.map((c) => ({
    category_id: c.id,
    category: c.name,
    budgeted: Number(getFormAmount(c.id)) || 0,
    spent: 0,
    projected_spent: 0,
    status: 'ok',
  }))
})

const categoryChartData = computed(() => {
  if (!isCreateMethodFlow.value || activeTab.value !== 'categorias') return chartData.value
  const labels = categories.value.map((c) => c.name)
  const values = categories.value.map((c) => Number(getFormAmount(c.id)) || 0)
  if (!values.some((v) => v > 0)) return null
  return {
    labels,
    datasets: [{ label: 'Presupuesto', data: values, backgroundColor: '#2563eb' }],
  }
})

const groupAmounts = computed(() => {
  const amounts = {}
  for (const g of configGroups.value) amounts[g.key] = 0
  for (const entry of formBudgets.value) {
    const cat = categories.value.find((c) => c.id === entry.id)
    if (!cat) continue
    const key = groupMapping.value[entry.id]
    if (key && amounts[key] !== undefined) {
      amounts[key] += Number(entry.amount) || 0
    }
  }
  return amounts
})

const summaryBudgetRows = computed(() =>
  formBudgets.value
    .filter((e) => Number(e.amount) > 0)
    .map((e) => {
      const cat = categories.value.find((c) => c.id === e.id)
      return { id: e.id, name: cat?.name || 'Categoría', amount: Number(e.amount) }
    })
)

function getFormAmount(id) {
  const entry = formBudgets.value.find((e) => e.id === id)
  return entry ? entry.amount : ''
}

function setFormAmount(id, value) {
  const amount = value === '' ? '' : Number(value)
  formBudgets.value = formBudgets.value.map((e) => e.id === id ? { ...e, amount } : e)
}

function initFormBudgets() {
  if (currentMode.value === 'create' && creationStep.value === 'manual') {
    formBudgets.value = categories.value.map((c) => ({ id: c.id, amount: '' }))
  } else if (currentMode.value === 'edit') {
    formBudgets.value = budgetItems.value.map((item) => ({ id: item.category_id, amount: Number(item.budgeted) || 0 }))
  } else {
    formBudgets.value = []
  }
}

async function handleSaveCreate() {
  formError.value = ''
  const payloads = formBudgets.value.filter((e) => e.amount !== '' && e.amount > 0).map((e) => ({ category_id: e.id, amount: e.amount }))
  if (creationStep.value === 'summary') {
    saving.value = true
    try {
      let created = 0
      for (const cat of categories.value) {
        const amt = Number(getFormAmount(cat.id))
        if (amt > 0) { await createBudget({ category_id: cat.id, amount: amt }); created++ }
      }
      if (created === 0) {
        formError.value = 'Ingresa al menos un monto o aplica un método antes de crear el presupuesto.'
        return
      }
      emit('saved')
      currentMode.value = 'view'
    } catch { formError.value = 'No pudimos guardar tu presupuesto. Intenta de nuevo.' } finally { saving.value = false }
    return
  }
  if (payloads.length === 0) { formError.value = 'Ingresa al menos un monto para crear tu presupuesto.'; return }
  saving.value = true
  try {
    for (const payload of payloads) { await createBudget(payload) }
    emit('saved')
    currentMode.value = 'view'
  } catch { formError.value = 'No pudimos guardar tu presupuesto. Intenta de nuevo.' } finally { saving.value = false }
}

async function handleSaveEdit() {
  formError.value = ''
  const payloads = formBudgets.value.filter((e) => e.amount !== '' && e.amount >= 0)
  if (payloads.length === 0) { formError.value = 'No hay cambios para guardar.'; return }
  saving.value = true
  try {
    for (const entry of payloads) { await editBudget(entry.id, entry.amount) }
    emit('saved')
    currentMode.value = 'view'
  } catch { formError.value = 'No pudimos guardar los cambios. Intenta de nuevo.' } finally { saving.value = false }
}

function enterEdit() { currentMode.value = 'edit'; initFormBudgets() }
function cancelEdit() { currentMode.value = 'view'; formBudgets.value = [] }

function close() {
  currentMode.value = props.mode
  activeTab.value = 'resumen'
  visitedResumen.value = false
  methodReady.value = false
  creationStep.value = 'method'
  activeMethodId.value = null
  resetMethodTab()
  formBudgets.value = []
  formError.value = ''
  applyMsg.value = ''
  emit('close')
}

watch(() => props.open, (val) => {
  if (val) {
    currentMode.value = props.mode
    activeMethodId.value = null
    applyMsg.value = ''
    resetMethodTab()
    if (props.mode === 'create') {
      creationStep.value = 'method'
      activeTab.value = 'metodo'
      loadPresets()
      loadConfig().then(() => { syncFromConfig() })
      loadBudgets().then(() => {
        loadCategories()
        initFormBudgets()
      })
    } else {
      activeTab.value = 'resumen'
      creationStep.value = 'method'
      loadBudgets().then(() => {
        initFormBudgets()
      })
      visitedResumen.value = true
      loadPresets()
      loadConfig().then(() => { syncFromConfig(); previewIncome.value = incomeAmount.value; methodReady.value = true })
    }
  } else {
    formError.value = ''
  }
}, { immediate: true })

function onKeydown(e) { if (e.key === 'Escape' && props.open) close() }
onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

function pct(item) { const budgeted = Number(item.budgeted) || 1; const spent = Number(item.spent) || 0; return Math.min(((spent / budgeted) * 100), 100).toFixed(1) }
function statusVariant(status) { const map = { ok: 'success', warning: 'warning', over: 'error' }; return map[status] || 'default' }
</script>

<style scoped>
.bdm-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: var(--spacing-md); }
.bdm-modal { background: var(--color-neutral-0); border-radius: var(--radius-lg); width: 100%; max-width: 900px; max-height: 90vh; display: flex; flex-direction: column; box-shadow: var(--shadow-lg); }
.bdm-header { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-lg); border-bottom: 1px solid var(--color-neutral-100); }
.bdm-title { font-family: var(--font-display); font-size: 1.1rem; font-weight: 600; margin: 0; }
.bdm-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 8px 12px; color: var(--color-neutral-500); min-width: 44px; min-height: 44px; display: inline-flex; align-items: center; justify-content: center; border-radius: var(--radius-sm); transition: transform var(--transition-fast); }
.bdm-close:hover { color: var(--color-neutral-900); background: var(--color-neutral-100); }
.bdm-close:active { transform: scale(0.94); }

.bdm-wizard { padding: var(--spacing-sm) var(--spacing-lg) var(--spacing-md); border-bottom: 1px solid var(--color-neutral-100); background: var(--color-neutral-50); display: flex; flex-direction: column; gap: 6px; }
.bdm-wizard-label { display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; font-weight: 600; color: var(--color-neutral-700); }
.bdm-wizard-pct { font-family: var(--font-mono); color: var(--color-primary-700); }
.bdm-wizard-track { height: 6px; background: var(--color-neutral-200); border-radius: 3px; overflow: hidden; }
.bdm-wizard-fill { height: 100%; background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-600)); border-radius: 3px; transition: width var(--transition-normal); }

.bdm-body { padding: var(--spacing-lg); overflow-y: auto; display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-hint { font-size: var(--font-size-sm); color: var(--color-neutral-500); margin: 0; }
.bdm-empty { text-align: center; padding: var(--spacing-xl) 0; color: var(--color-neutral-400); font-size: var(--font-size-sm); }
.bdm-alert { background: var(--color-warning-50); color: var(--color-warning-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: 0.85rem; }
.bdm-chart { height: 220px; }
.bdm-table-wrap { overflow-x: auto; }
.bdm-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.bdm-table th, .bdm-table td { padding: 10px 8px; text-align: left; border-bottom: 1px solid var(--color-neutral-100); }
.bdm-table th { font-weight: 600; color: var(--color-neutral-500); font-size: 0.75rem; text-transform: uppercase; }
.bdm-tabs { display: flex; gap: 4px; padding: 0 var(--spacing-md); border-bottom: 1px solid var(--color-neutral-100); }
.bdm-tab { flex: 1 1 0; min-height: 44px; padding: var(--spacing-sm) var(--spacing-xs); background: none; border: none; border-bottom: 2px solid transparent; font-size: 0.85rem; font-weight: 600; color: var(--color-neutral-500); cursor: pointer; transition: color var(--transition-fast), border-color var(--transition-fast); }
.bdm-tab:hover { color: var(--color-neutral-900); }
.bdm-tab.active { color: var(--color-primary-700); border-bottom-color: var(--color-primary-600); }
.bdm-tab:focus-visible { outline: 2px solid var(--color-primary-500); outline-offset: -2px; border-radius: var(--radius-sm); }
.bdm-panel { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-tab-enter-active, .bdm-tab-leave-active { transition: opacity 200ms ease, transform 200ms ease; }
.bdm-tab-enter-from { opacity: 0; transform: translateX(12px); }
.bdm-tab-leave-to { opacity: 0; transform: translateX(-12px); }
@media (prefers-reduced-motion: reduce) { .bdm-tab-enter-active, .bdm-tab-leave-active { transition: none; } .bdm-progress-fill, .bdm-wizard-fill { transition: none; } }
.bdm-kpis { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-kpi-row { display: flex; justify-content: space-between; align-items: baseline; gap: var(--spacing-md); }
.bdm-kpi-label { font-size: 0.85rem; color: var(--color-neutral-500); }
.bdm-kpi-value { font-family: var(--font-mono); font-size: 1rem; font-weight: 700; color: var(--color-neutral-900); }
.bdm-kpi-text { font-size: 0.85rem; color: var(--color-neutral-700); }
.bdm-kpi-muted { font-weight: 500; color: var(--color-neutral-400); font-size: 0.85rem; }
.bdm-progress-track { height: 10px; background: var(--color-neutral-100); border-radius: 5px; overflow: hidden; }
.bdm-progress-fill { height: 100%; background: var(--color-primary-500); border-radius: 5px; transition: width 200ms ease; }
.bdm-status-row { display: flex; align-items: center; gap: var(--spacing-sm); }
.bdm-status-text { font-size: 0.85rem; color: var(--color-neutral-700); }
.bdm-link { background: none; border: none; color: var(--color-primary-600); cursor: pointer; font-size: 0.8rem; font-weight: 500; padding: 4px 0; transition: opacity var(--transition-fast); }
.bdm-link:hover { text-decoration: underline; }
.bdm-link:active { opacity: 0.7; }
.bdm-group-name { display: block; font-size: 0.85rem; color: var(--color-neutral-700); margin-bottom: 2px; }
.bdm-group-select { padding: var(--spacing-xs) var(--spacing-sm); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); font-size: 0.85rem; background: var(--color-neutral-0); color: var(--color-neutral-800); min-height: 44px; }
.bdm-group-select:focus { outline: none; border-color: var(--color-primary-500); box-shadow: 0 0 0 3px var(--color-primary-100); }
.bdm-group-btns { display: flex; gap: var(--spacing-sm); margin-top: 4px; }
.bdm-onboard { background: var(--color-neutral-50); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-md); padding: var(--spacing-sm) var(--spacing-md); }
.bdm-onboard-title { font-size: 0.8rem; font-weight: 600; color: var(--color-neutral-700); margin: 0 0 6px; }
.bdm-onboard-steps { display: flex; flex-wrap: wrap; gap: 4px 16px; margin: 0; padding: 0; list-style: none; }
.bdm-onboard-step { display: flex; align-items: center; gap: 6px; font-size: 0.78rem; color: var(--color-neutral-400); }
.bdm-onboard-step.done { color: var(--color-neutral-600); }
.bdm-onboard-step.current { color: var(--color-primary-700); font-weight: 600; }
.bdm-onboard-dot { font-size: 0.7rem; }
.bdm-hero { display: flex; flex-direction: column; gap: var(--spacing-xs); margin-bottom: var(--spacing-sm); }
.bdm-hero-title { font-family: var(--font-display); font-size: 1.25rem; font-weight: 700; color: var(--color-neutral-900); margin: 0; }
.bdm-hero-sub { font-size: 0.95rem; color: var(--color-neutral-500); margin: 0; }
.bdm-hero-note { background: var(--color-primary-50); border: 1px solid var(--color-primary-100); color: var(--color-primary-700); font-size: 0.85rem; padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); margin: 0; }
.bdm-hero-footnote { font-size: 0.8rem; color: var(--color-neutral-400); margin: 0; }
.bdm-onboarding-options { display: flex; flex-direction: column; gap: var(--spacing-md); margin: var(--spacing-sm) 0; }
.bdm-onboarding-option { display: flex; flex-direction: column; gap: var(--spacing-xs); text-align: left; background: var(--color-neutral-0); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); padding: var(--spacing-md); cursor: pointer; transition: border-color var(--transition-fast), box-shadow var(--transition-fast); min-height: 44px; position: relative; }
.bdm-onboarding-option:hover { border-color: var(--color-primary-500); }
.bdm-onboarding-option--primary { border-color: var(--color-primary-600); background: var(--color-primary-50); }
.bdm-onboarding-option--primary:hover { border-color: var(--color-primary-700); box-shadow: 0 0 0 3px var(--color-primary-100); }
.bdm-onboarding-option-icon { font-size: 1.5rem; }
.bdm-onboarding-option-title { font-size: 1rem; font-weight: 700; color: var(--color-neutral-900); }
.bdm-onboarding-option-desc { font-size: 0.85rem; color: var(--color-neutral-500); }
.bdm-onboarding-option-badge { position: absolute; top: var(--spacing-md); right: var(--spacing-md); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-primary-700); background: var(--color-primary-100); padding: 2px 8px; border-radius: 999px; align-self: flex-start; }
.bdm-summary-section { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-summary-h3 { font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: var(--color-neutral-900); margin: 0; }
.bdm-summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-sm); }
.bdm-summary-card { background: var(--color-neutral-50); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-md); padding: var(--spacing-md); display: flex; flex-direction: column; gap: var(--spacing-xs); }
.bdm-summary-label { font-size: 0.75rem; color: var(--color-neutral-500); text-transform: uppercase; font-weight: 600; }
.bdm-summary-value { font-size: 1rem; font-weight: 700; color: var(--color-neutral-900); font-family: var(--font-mono); }
.bdm-form-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.bdm-form-row { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-50); }
.bdm-form-row:last-child { border-bottom: none; }
.bdm-form-label { font-size: 0.85rem; font-weight: 500; color: var(--color-neutral-700); min-width: 140px; }
.bdm-form-input-wrap { display: flex; align-items: center; gap: 4px; }
.bdm-form-prefix { font-size: 0.85rem; color: var(--color-neutral-400); font-family: var(--font-mono); }
.bdm-form-input { width: 140px; padding: var(--spacing-sm); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); font-size: 0.85rem; font-family: var(--font-mono); text-align: right; transition: border-color var(--transition-fast); }
.bdm-form-input:focus { outline: none; border-color: var(--color-primary-500); box-shadow: 0 0 0 3px var(--color-primary-100); }
.bdm-form-input::-webkit-inner-spin-button, .bdm-form-input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.bdm-form-input[type=number] { -moz-appearance: textfield; }
.bdm-error { background: var(--color-error-50); color: var(--color-error-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: 0.85rem; }
.bdm-form-help { font-size: 0.75rem; color: var(--color-neutral-400); margin: var(--spacing-xs) 0 0; }
.bdm-footer { display: flex; justify-content: space-between; padding-top: var(--spacing-md); border-top: 1px solid var(--color-neutral-100); }
.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; transition: transform var(--transition-fast); min-height: 44px; }
.btn:active:not(:disabled) { transform: scale(0.97); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--color-primary-600); color: var(--color-neutral-0); transition: transform var(--transition-fast); }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
.btn-primary:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }
@media (prefers-reduced-motion: reduce) { .bdm-method-card { transition: none; } .bdm-progress-fill { transition: none; } }
@media (min-width: 768px) { .bdm-tabs { justify-content: center; padding: 0 var(--spacing-lg); } .bdm-tab { flex: 0 0 auto; min-width: 150px; } .bdm-summary-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 768px) { .bdm-summary-grid { grid-template-columns: 1fr; } }
</style>

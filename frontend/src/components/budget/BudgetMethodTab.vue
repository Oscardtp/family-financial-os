<template>
  <div class="bdm-method-tab">
    <p v-if="currentMethod && !suppressCurrentHint" class="bdm-hint">Método actual: <strong>{{ currentMethod }}</strong></p>

    <!-- STEP 1: catalog -->
    <div v-if="step === 'catalog'">
      <template v-if="!showAll">
        <div class="bmt-section-head">
          <h4 class="bmt-section-title">Recomendados</h4>
        </div>
        <div class="bdm-methods bdm-methods--recommended" data-testid="recommended-methods">
          <button
            v-for="m in recommendedMethods"
            :key="m.id"
            class="bdm-method-card bdm-method-card--recommended"
            :class="{ selected: selectedId === m.id }"
            :aria-pressed="selectedId === m.id"
            data-testid="method-card"
            @click="selectMethod(m)"
          >
            <span class="bdm-method-top">
              <span class="bdm-method-name">{{ m.name }}</span>
              <span class="bdm-method-top-right">
                <span v-if="selectedId === m.id" class="bdm-method-check" aria-hidden="true">✓</span>
                <span v-if="m.id === '50_30_20'" class="bdm-method-badge">Recomendada</span>
              </span>
            </span>
            <span class="bdm-method-desc">{{ recommendedCopy[m.id] || m.description }}</span>
            <span class="bdm-method-bars" aria-hidden="true">
              <span
                v-for="g in m.groups"
                :key="g.key"
                class="bdm-method-bar"
                :style="{ width: g.pct + '%' }"
                :title="`${g.label} ${g.pct}%`"
              />
            </span>
            <span class="bdm-method-groups">{{ m.groups.map((g) => `${g.label} ${g.pct}%`).join(' · ') }}</span>
          </button>
        </div>

        <button
          class="bdm-link bdm-show-all"
          data-testid="show-all-methods"
          @click="showAll = true"
        >
          Ver otros {{ Math.max(methods.length - recommendedMethods.length, 0) }} métodos
        </button>
      </template>

      <template v-else>
        <div class="bmt-section-head">
          <h4 class="bmt-section-title">Todos los métodos</h4>
          <button class="bdm-link" data-testid="show-recommended-only" @click="showAll = false">
            Ver solo recomendados
          </button>
        </div>
        <div class="bdm-methods" data-testid="all-methods">
          <button
            v-for="m in methods"
            :key="m.id"
            class="bdm-method-card"
            :class="{ selected: selectedId === m.id }"
            :aria-pressed="selectedId === m.id"
            data-testid="method-card"
            @click="selectMethod(m)"
          >
            <span class="bdm-method-name">{{ m.name }}</span>
            <span v-if="selectedId === m.id" class="bdm-method-check" aria-hidden="true">✓</span>
            <span class="bdm-method-desc">{{ m.description }}</span>
            <span class="bdm-method-bars" aria-hidden="true">
              <span
                v-for="g in m.groups"
                :key="g.key"
                class="bdm-method-bar"
                :style="{ width: g.pct + '%' }"
                :title="`${g.label} ${g.pct}%`"
              />
            </span>
            <span class="bdm-method-groups">{{ m.groups.map((g) => `${g.label} ${g.pct}%`).join(' · ') }}</span>
          </button>
        </div>
      </template>

      <div v-if="selectedMethod" ref="incomeSection" class="bmt-catalog-extra" data-testid="income-section">
        <p class="bmt-selection-callout" role="status" data-testid="selection-callout">
          Perfecto. Ahora ingresa cuánto recibes al mes.
        </p>

        <div class="bmt-catalog-income">
          <label class="bdm-form-label" for="catalog-income">Ingreso de referencia</label>
          <div class="bdm-input-wrap">
            <span class="bdm-prefix">$</span>
            <input
              id="catalog-income"
              ref="incomeInput"
              type="number"
              class="bdm-form-input bdm-form-input--pct"
              min="0"
              step="10000"
              placeholder="0"
              v-model="catalogIncome"
            />
          </div>
        </div>

        <div class="bmt-preview-cta">
          <div class="bmt-preview-cta-text">
            <h5 class="bmt-preview-cta-title">Vista previa</h5>
            <p class="bmt-preview-cta-sub">Mira cómo se distribuiría tu ingreso antes de aplicarlo.</p>
          </div>
          <button class="btn btn-primary bmt-preview-cta-btn" data-testid="preview-btn" @click="showPreview">
            <Sparkles :size="16" aria-hidden="true" />
            Ver cómo quedaría mi dinero
          </button>
        </div>
      </div>
    </div>

    <!-- STEP 2: preview -->
    <div v-if="step === 'preview'" class="bdm-preview-wrap">
      <div class="bdm-preview-visual" data-testid="method-preview">
        <h4 class="bdm-preview-headline">Así quedaría tu dinero</h4>
        <p v-if="incomeForPreview" class="bdm-preview-sub">
          Con un ingreso de referencia de ${{ fmt(incomeForPreview) }}
        </p>

        <div class="bdm-preview-rows">
          <div v-for="g in previewAllocations" :key="g.key" class="bdm-preview-row">
            <div class="bdm-preview-row-left">
              <span class="bdm-preview-pct">{{ g.pct }}%</span>
              <span class="bdm-preview-label">{{ g.label }}</span>
            </div>
            <span class="bdm-preview-amount" :data-preview-key="g.key">
              <template v-if="g.amount !== null && g.amount !== undefined">${{ fmt(g.amount) }}</template>
              <template v-else>—</template>
            </span>
          </div>
        </div>

        <span class="bdm-method-bars bdm-preview-bars" aria-hidden="true">
          <span
            v-for="g in editableGroups"
            :key="g.key"
            class="bdm-method-bar"
            :style="{ width: g.pct + '%' }"
          />
        </span>

        <p class="bdm-sum" :class="{ ok: isValid, bad: !isValid }" role="status" data-testid="sum-display">
          Suma: {{ currentSum }}% {{ sumValid ? '✓' : '— debe ser 100%' }}
        </p>

        <div class="bdm-editor-toggle">
          <button class="bdm-link" @click="showEditor = !showEditor">
            {{ showEditor ? 'Ocultar personalización' : 'Personalizar porcentajes' }}
          </button>
        </div>

        <div v-if="showEditor" class="bdm-editor-panel">
          <div class="bdm-group-list">
            <div v-for="g in editableGroups" :key="g.key" class="bdm-group-row">
              <span class="bdm-group-label">{{ g.label }}</span>
              <div class="bdm-input-wrap">
                <input
                  type="number"
                  class="bdm-form-input bdm-form-input--pct"
                  :value="g.pct"
                  @input="onPctInput(g.key, $event.target.value)"
                  min="0"
                  max="100"
                  step="1"
                />
              </div>
              <span class="bdm-group-pct">{{ g.pct }}%</span>
            </div>
          </div>
          <BudgetMethodEditor
            :groups="editableGroups"
            @update="onEditorUpdate"
          />
        </div>

        <p v-if="applyMsg" class="bmt-ok" role="status" data-testid="apply-msg">{{ applyMsg }}</p>

        <div class="bdm-row-btns bdm-preview-cta">
          <button class="btn bdm-btn-back" @click="backToCatalog">← Elegir otro método</button>
          <button class="btn btn-primary bdm-btn-apply" data-testid="apply-method" @click="apply" :disabled="!isValid">
            Aplicar método
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { Sparkles } from 'lucide-vue-next'
import BudgetMethodEditor from './BudgetMethodEditor.vue'
import {
  listBudgetMethods,
  listRecommendedBudgetMethods,
  RECOMMENDED_METHOD_COPY,
} from '@/constants/budgetMethods'
import { useBudgetMethod } from '@/composables/useBudgetMethod'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps({
  currentMethod: { type: String, default: '' },
  creationStep: { type: String, default: '' },
  suppressCurrentHint: { type: Boolean, default: false },
})

const emit = defineEmits(['apply'])

const { fmt } = useCurrency()
const { fetchPreview, preview, previewLoading } = useBudgetMethod()

const methods = listBudgetMethods()
const recommendedMethods = listRecommendedBudgetMethods()
const recommendedCopy = RECOMMENDED_METHOD_COPY
const step = ref('catalog')
const selectedId = ref(null)
const editableGroups = ref([])
const showEditor = ref(false)
const applyMsg = ref('')
const catalogIncome = ref('')
const incomeInput = ref(null)
const showAll = ref(false)
const incomeSection = ref(null)

const selectedMethod = computed(() => methods.find(m => m.id === selectedId.value) || null)

const currentSum = computed(() => editableGroups.value.reduce((acc, g) => acc + (Number(g.pct) || 0), 0))
const sumValid = computed(() => editableGroups.value.length > 0 && currentSum.value === 100)
const isValid = computed(() => sumValid.value)

const incomeForPreview = computed(() => Number(catalogIncome.value) || 0)

const previewAllocations = computed(() => {
  const groups = editableGroups.value
  const fromApi = preview.value && Array.isArray(preview.value.allocations)
    ? preview.value.allocations
    : null
  return groups.map((g) => {
    const api = fromApi ? fromApi.find((a) => a.key === g.key) : null
    return {
      key: g.key,
      label: g.label,
      pct: Number(g.pct) || 0,
      amount: api && api.amount !== undefined && api.amount !== null ? Number(api.amount) : null,
    }
  })
})

function prefersReducedMotion() {
  return typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

function scrollToIncome() {
  const el = incomeSection.value
  if (!el || typeof el.scrollIntoView !== 'function') return
  el.scrollIntoView({
    behavior: prefersReducedMotion() ? 'auto' : 'smooth',
    block: 'start',
  })
}

function selectMethod(m) {
  selectedId.value = m.id
  editableGroups.value = m.groups.map(g => ({ ...g }))
  showEditor.value = false
  applyMsg.value = ''
  step.value = 'catalog'
  nextTick(() => {
    scrollToIncome()
  })
}

async function showPreview() {
  if (!selectedMethod.value) return
  editableGroups.value = selectedMethod.value.groups.map(g => ({ ...g }))
  step.value = 'preview'
  applyMsg.value = ''
  showEditor.value = false
  const income = Number(catalogIncome.value) || 0
  if (income > 0) {
    try {
      await fetchPreview(income, editableGroups.value)
    } catch { /* preview amounts optional; pct view still works */ }
  }
}

function backToCatalog() {
  step.value = 'catalog'
  applyMsg.value = ''
}

function onPctInput(key, value) {
  const g = editableGroups.value.find(x => x.key === key)
  if (g) g.pct = Number(value)
}

function onEditorUpdate(groups) {
  editableGroups.value = groups
}

function apply() {
  if (!isValid.value || !selectedMethod.value) return
  emit('apply', {
    methodId: selectedMethod.value.id,
    methodName: selectedMethod.value.name,
    groups: editableGroups.value.map(g => ({ key: g.key, label: g.label, pct: Number(g.pct) })),
    incomeAmount: catalogIncome.value,
  })
  applyMsg.value = 'Método guardado. Tus presupuestos existentes no cambiaron.'
}

function reset() {
  step.value = 'catalog'
  selectedId.value = null
  editableGroups.value = []
  showEditor.value = false
  applyMsg.value = ''
  catalogIncome.value = ''
  showAll.value = false
}

defineExpose({ reset })
</script>

<style scoped>
.bdm-method-tab { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-hint { font-size: var(--font-size-sm); color: var(--color-neutral-500); margin: 0; }
.bmt-section-head { display: flex; justify-content: space-between; align-items: center; gap: var(--spacing-sm); margin-bottom: var(--spacing-sm); }
.bmt-section-title { font-size: 0.85rem; font-weight: 700; color: var(--color-neutral-800); margin: 0; text-transform: uppercase; letter-spacing: 0.04em; }
.bdm-methods { display: grid; grid-template-columns: 1fr; gap: var(--spacing-sm); }
.bdm-methods--recommended { grid-template-columns: 1fr; }
.bdm-method-card { display: flex; flex-direction: column; gap: var(--spacing-xs); text-align: left; background: var(--color-neutral-0); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); padding: var(--spacing-md); cursor: pointer; transition: border-color var(--transition-fast), box-shadow var(--transition-fast), transform var(--transition-fast); position: relative; }
.bdm-method-card:hover { border-color: var(--color-primary-500); box-shadow: 0 4px 12px rgba(0,0,0,0.06); transform: translateY(-1px); }
.bdm-method-card:active { transform: scale(0.99); }
.bdm-method-card.selected { border-color: var(--color-primary-600); border-width: 2px; box-shadow: 0 0 0 3px var(--color-primary-100); }
.bdm-method-card:focus-visible { outline: 2px solid var(--color-primary-500); outline-offset: 2px; }
.bdm-method-card--recommended { border-color: var(--color-neutral-200); }
.bdm-method-top { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-sm); }
.bdm-method-top-right { display: flex; align-items: center; gap: var(--spacing-xs); }
.bdm-method-check { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; background: var(--color-primary-600); color: var(--color-neutral-0); font-size: 0.7rem; font-weight: 700; animation: bmt-check-in 200ms ease; }
@keyframes bmt-check-in { from { transform: scale(0); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.bdm-method-name { font-size: 0.95rem; font-weight: 700; color: var(--color-neutral-900); }
.bdm-method-badge { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-primary-700); background: var(--color-primary-100); padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
.bdm-method-desc { font-size: 0.85rem; color: var(--color-neutral-500); }
.bdm-method-bars { display: flex; height: 10px; border-radius: 5px; overflow: hidden; background: var(--color-neutral-100); width: 100%; }
.bdm-method-bar { height: 100%; background: var(--color-primary-600); }
.bdm-method-bar:nth-child(2) { opacity: 0.75; }
.bdm-method-bar:nth-child(3) { opacity: 0.55; }
.bdm-method-bar:nth-child(4) { opacity: 0.42; }
.bdm-method-bar:nth-child(5) { opacity: 0.32; }
.bdm-method-bar:nth-child(6) { opacity: 0.24; }
.bdm-method-groups { font-size: 0.8rem; color: var(--color-neutral-500); }
.bdm-show-all { align-self: flex-start; margin-top: var(--spacing-xs); }
.bdm-preview-wrap { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-preview-visual { background: var(--color-neutral-50); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-lg); padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-preview-headline { font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; color: var(--color-neutral-900); margin: 0; }
.bdm-preview-sub { font-size: 0.9rem; color: var(--color-neutral-500); margin: 0; }
.bdm-preview-rows { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.bdm-preview-row { display: flex; justify-content: space-between; align-items: center; gap: var(--spacing-md); padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-100); }
.bdm-preview-row:last-child { border-bottom: none; }
.bdm-preview-row-left { display: flex; align-items: center; gap: var(--spacing-sm); }
.bdm-preview-pct { font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; color: var(--color-primary-700); background: var(--color-primary-100); padding: 2px 8px; border-radius: 999px; min-width: 44px; text-align: center; }
.bdm-preview-label { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-800); }
.bdm-preview-amount { font-family: var(--font-mono); font-size: 1.1rem; font-weight: 700; color: var(--color-neutral-900); }
.bdm-preview-bars { height: 12px; border-radius: 6px; }
.bdm-preview-cta { justify-content: space-between; align-items: center; width: 100%; }
.bdm-btn-apply { min-width: 160px; min-height: 48px; font-size: 0.95rem; }
.bdm-btn-back { background: none; color: var(--color-neutral-600); }
.bdm-subtitle { font-size: 0.9rem; font-weight: 700; color: var(--color-neutral-800); margin: 0; }
.bdm-preview { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bdm-distribucion { font-size: 0.9rem; font-weight: 700; color: var(--color-neutral-800); margin: 0; }
.bdm-group-list { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.bdm-group-row { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--color-neutral-50); }
.bdm-group-row:last-child { border-bottom: none; }
.bdm-group-label { font-size: 0.85rem; color: var(--color-neutral-700); }
.bdm-group-pct { font-family: var(--font-mono); font-size: 0.9rem; font-weight: 700; color: var(--color-neutral-900); }
.bdm-editor-toggle { margin-top: var(--spacing-xs); }
.bdm-editor-panel { display: flex; flex-direction: column; gap: var(--spacing-sm); padding-top: var(--spacing-sm); border-top: 1px dashed var(--color-neutral-200); }
.bdm-link { background: none; border: none; color: var(--color-primary-600); cursor: pointer; font-size: 0.85rem; font-weight: 500; padding: var(--spacing-sm) var(--spacing-xs); min-height: 44px; display: inline-flex; align-items: center; }
.bdm-link:hover { text-decoration: underline; }
.bdm-row-btns { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.bmt-ok { background: var(--color-success-50); color: var(--color-success-700); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); font-size: 0.85rem; margin: 0; }
.bdm-sum { font-size: 0.85rem; font-weight: 600; margin: 0; }
.bdm-sum.ok { color: var(--color-success-700); }
.bdm-sum.bad { color: var(--color-error-600); }
.bdm-prefix { font-size: 0.85rem; color: var(--color-neutral-400); font-family: var(--font-mono); }
.bdm-input-wrap { display: flex; align-items: center; gap: 4px; }
.bdm-form-input { width: 140px; padding: var(--spacing-sm); border: 1px solid var(--color-neutral-200); border-radius: var(--radius-md); font-size: 0.85rem; font-family: var(--font-mono); text-align: right; transition: border-color var(--transition-fast); }
.bdm-form-input:focus { outline: none; border-color: var(--color-primary-500); box-shadow: 0 0 0 3px var(--color-primary-100); }
.bdm-form-input::-webkit-inner-spin-button, .bdm-form-input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.bdm-form-input[type=number] { -moz-appearance: textfield; }
.bdm-form-input--pct { width: 90px; }
.bdm-form-label { font-size: 0.85rem; font-weight: 500; color: var(--color-neutral-700); min-width: 140px; }
.bmt-catalog-extra { display: flex; flex-direction: column; gap: var(--spacing-sm); padding-top: var(--spacing-sm); border-top: 1px solid var(--color-neutral-100); margin-top: var(--spacing-xs); }
.bmt-selection-callout { background: var(--color-primary-50); border: 1px solid var(--color-primary-100); color: var(--color-primary-700); font-size: 0.9rem; font-weight: 600; padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--radius-md); margin: 0; animation: bmt-fade-in 200ms ease; }
@keyframes bmt-fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.bmt-preview-cta { display: flex; flex-direction: column; gap: var(--spacing-sm); background: var(--color-neutral-50); border: 1px solid var(--color-neutral-100); border-radius: var(--radius-lg); padding: var(--spacing-md); }
.bmt-preview-cta-text { display: flex; flex-direction: column; gap: 2px; }
.bmt-preview-cta-title { font-size: 0.95rem; font-weight: 700; color: var(--color-neutral-900); margin: 0; }
.bmt-preview-cta-sub { font-size: 0.85rem; color: var(--color-neutral-500); margin: 0; }
.bmt-preview-cta-btn { width: 100%; min-height: 48px; font-size: 0.95rem; gap: var(--spacing-xs); }
.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: transform var(--transition-fast); min-height: 44px; }
.btn:active:not(:disabled) { transform: scale(0.97); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--color-primary-600); color: var(--color-neutral-0); }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
@media (prefers-reduced-motion: reduce) {
  .bdm-method-card { transition: none; }
  .bdm-method-card:hover { transform: none; box-shadow: none; }
  .bdm-method-check { animation: none; }
  .bmt-selection-callout { animation: none; }
}
@media (min-width: 768px) {
  .bdm-methods { grid-template-columns: 1fr 1fr; }
  .bdm-methods--recommended { grid-template-columns: 1fr 1fr 1fr; }
}
</style>

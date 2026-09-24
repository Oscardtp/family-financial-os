import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mount } from '@vue/test-utils'

const mockFmt = (v) => Number(v || 0).toLocaleString('es-CO')

const mockBudgetItems = [
  { category_id: 'cat-1', category: 'Alimentacion', budgeted: 500000, spent: 350000, projected_spent: 400000, status: 'ok' },
  { category_id: 'cat-2', category: 'Transporte', budgeted: 200000, spent: 180000, projected_spent: 210000, status: 'warning' },
]

const mockCategories = [
  { id: 'cat-3', name: 'Entretenimiento', type: 'expense' },
  { id: 'cat-4', name: 'Salud', type: 'expense' },
]

const mockPresets = [
  { id: '50_30_20', name: '50/30/20', description: 'El clásico', groups: [{ key: 'necesidades', label: 'Necesidades', pct: 50 }, { key: 'gustos', label: 'Gustos', pct: 30 }, { key: 'ahorro', label: 'Ahorro', pct: 20 }] },
  { id: '70_20_10', name: '70/20/10', description: 'Ahorro prioridad', groups: [{ key: 'gastos', label: 'Gastos', pct: 70 }, { key: 'ahorro', label: 'Ahorro', pct: 20 }, { key: 'deuda_donacion', label: 'Deuda/Donación', pct: 10 }] },
  { id: '60_40', name: '60/40', description: 'Simple', groups: [{ key: 'gastos_fijos', label: 'Gastos fijos', pct: 60 }, { key: 'libre', label: 'Libre', pct: 40 }] },
  { id: '6_jarras', name: '6 Jarras', description: 'Seis destinos', groups: [{ key: 'necesidades', label: 'Necesidades', pct: 55 }, { key: 'ahorro_largo', label: 'Ahorro largo plazo', pct: 10 }, { key: 'educacion', label: 'Educación', pct: 10 }, { key: 'diversion', label: 'Diversión', pct: 10 }, { key: 'libertad', label: 'Libertad financiera', pct: 10 }, { key: 'donacion', label: 'Donación', pct: 5 }] },
  { id: '80_20', name: '80/20', description: 'Págate primero', groups: [{ key: 'gastos', label: 'Gastos', pct: 80 }, { key: 'ahorro', label: 'Ahorro', pct: 20 }] },
  { id: '30_30_30_10', name: '30/30/30/10', description: 'Equilibrio', groups: [{ key: 'vivienda', label: 'Vivienda', pct: 30 }, { key: 'comida_transporte', label: 'Comida/transporte', pct: 30 }, { key: 'ahorro_deuda', label: 'Ahorro/deuda', pct: 30 }, { key: 'libre', label: 'Libre', pct: 10 }] },
  { id: '75_15_10', name: '75/15/10', description: 'Tres cuartos', groups: [{ key: 'gastos', label: 'Gastos', pct: 75 }, { key: 'ahorro', label: 'Ahorro', pct: 15 }, { key: 'deuda', label: 'Deuda', pct: 10 }] },
  { id: '40_30_20_10', name: '40/30/20/10', description: 'En cuatro', groups: [{ key: 'necesidades', label: 'Necesidades', pct: 40 }, { key: 'gustos', label: 'Gustos', pct: 30 }, { key: 'ahorro', label: 'Ahorro', pct: 20 }, { key: 'donacion', label: 'Donación', pct: 10 }] },
  { id: '50_50', name: '50/50', description: 'Mitad y mitad', groups: [{ key: 'fijos', label: 'Fijos', pct: 50 }, { key: 'variables', label: 'Variables', pct: 50 }] },
  { id: '70_30', name: '70/30', description: 'Con calma', groups: [{ key: 'gastos', label: 'Gastos', pct: 70 }, { key: 'ahorro', label: 'Ahorro', pct: 30 }] },
  { id: '33_33_33', name: '33/33/33', description: 'Tres partes', groups: [{ key: 'necesidades', label: 'Necesidades', pct: 34 }, { key: 'ahorro', label: 'Ahorro', pct: 33 }, { key: 'gustos', label: 'Gustos', pct: 33 }] },
]

const configuredState = () => ({
  method_type: '50_30_20',
  groups: [
    { key: 'necesidades', label: 'Necesidades', pct: 50 },
    { key: 'gustos', label: 'Gustos', pct: 30 },
    { key: 'ahorro', label: 'Ahorro', pct: 20 },
  ],
  category_groups: { 'cat-1': 'necesidades' },
  reference_income_source: 'manual',
  reference_income_amount: '5000000',
})

const methodState = vi.hoisted(() => ({
  config: null,
  loadPresets: vi.fn(),
  loadConfig: vi.fn(),
  saveConfig: vi.fn(),
  fetchPreview: vi.fn(),
}))

const mocks = vi.hoisted(() => ({
  loadBudgets: vi.fn().mockResolvedValue(),
  createBudget: vi.fn().mockResolvedValue(),
  editBudget: vi.fn().mockResolvedValue(),
  loadCategories: vi.fn().mockResolvedValue(),
  deleteBudget: vi.fn().mockResolvedValue(),
}))

vi.mock('@/composables/useBudgets', () => ({
  useBudgets: () => ({
    loading: ref(false),
    error: ref(''),
    month: ref(9),
    year: ref(2026),
    monthLabel: ref('Septiembre 2026'),
    statusData: ref({ items: mockBudgetItems }),
    rawBudgets: ref([]),
    budgetItems: ref(mockBudgetItems),
    unbudgetedCategories: ref(mockCategories),
    chartData: ref(null),
    chartOptions: {},
    budgetProjection: ref(null),
    budgetTotals: ref({ planificado: 700000, ejecutado: 530000, disponible: 170000, proyectado: 600000 }),
    budgetAlertMessage: ref(''),
    statusLabel: (s) => ({ ok: 'Vamos bien', warning: 'Cuidado', over: 'Nos pasamos' })[s] || s,
    loadBudgets: mocks.loadBudgets,
    loadCategories: mocks.loadCategories,
    createBudget: mocks.createBudget,
    editBudget: mocks.editBudget,
    deleteBudget: mocks.deleteBudget,
  }),
}))

vi.mock('@/composables/useBudgetMethod', () => ({
  useBudgetMethod: () => ({
    presets: ref(mockPresets),
    presetsLoading: ref(false),
    config: ref(methodState.config),
    configLoading: ref(false),
    methodSaving: ref(false),
    preview: ref(null),
    previewLoading: ref(false),
    methodError: ref(''),
    loadPresets: methodState.loadPresets.mockResolvedValue(mockPresets),
    loadConfig: methodState.loadConfig.mockImplementation(async () => methodState.config),
    saveConfig: methodState.saveConfig.mockImplementation(async (p) => {
      methodState.config = { ...p, updated_at: '2026-09-22T12:00:00' }
      return methodState.config
    }),
    fetchPreview: methodState.fetchPreview.mockImplementation(async (income, groups) => ({
      income_amount: String(income),
      allocations: groups.map((g) => ({ key: g.key, label: g.label, pct: Number(g.pct), amount: String(Math.round(Number(income) * Number(g.pct) / 100)) })),
    })),
    resetPreview: vi.fn(),
  }),
}))

vi.mock('@/composables/useCurrency', () => ({
  useCurrency: () => ({ fmt: mockFmt, fmtFull: mockFmt }),
}))

vi.mock('vue-chartjs', () => ({
  Bar: { template: '<div class="bar-chart" />' },
}))

vi.mock('lucide-vue-next', () => ({
  AlertTriangle: { template: '<span />' },
  X: { template: '<span />' },
  Sparkles: { template: '<span />' },
}))

const toastMock = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn(),
  warning: vi.fn(),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => toastMock,
}))

vi.mock('@/components/FocusTrap.vue', () => ({
  default: { template: '<div><slot /></div>', props: ['visible'] },
}))

vi.mock('@/components/SkeletonLoader.vue', () => ({
  default: { template: '<div class="skeleton" />', props: ['variant', 'width', 'height'] },
}))

vi.mock('@/components/StatusBadge.vue', () => ({
  default: { template: '<span class="badge" />', props: ['label', 'variant'] },
}))

const BudgetDetailModal = (await import('@/components/budget/BudgetDetailModal.vue')).default

function mountModal(props = {}) {
  return mount(BudgetDetailModal, {
    props: { open: true, mode: 'view', ...props },
    global: { stubs: { teleport: true } },
  })
}

async function selectTab(wrapper, label) {
  const tab = wrapper.findAll('[role="tab"]').find((t) => t.text() === label)
  expect(tab).toBeTruthy()
  await tab.trigger('click')
  await new Promise((r) => setTimeout(r, 60))
  await wrapper.vm.$nextTick()
}

async function flush(wrapper) {
  await new Promise((r) => setTimeout(r, 30))
  await wrapper.vm.$nextTick()
}

async function openCreateHero(wrapper) {
  await flush(wrapper)
  expect(wrapper.find('[data-testid="onboard-method"]').exists()).toBe(true)
}

async function goToCatalog(wrapper) {
  await wrapper.find('[data-testid="onboard-method"]').trigger('click')
  await flush(wrapper)
}

describe('BudgetDetailModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    methodState.config = null
  })

  it('does not render when open=false', () => {
    const wrapper = mountModal({ open: false })
    expect(wrapper.find('.bdm-modal').exists()).toBe(false)
  })

  it('renders modal when open=true', () => {
    const wrapper = mountModal()
    expect(wrapper.find('.bdm-modal').exists()).toBe(true)
  })

  it('loads budgets when opened', () => {
    mountModal()
    expect(mocks.loadBudgets).toHaveBeenCalled()
  })

  describe('VIEW mode', () => {
    it('shows Resumen KPIs by default, not the table', () => {
      const wrapper = mountModal({ mode: 'view' })
      expect(wrapper.text()).toContain('Gastado')
      expect(wrapper.text()).toContain('Disponible')
      expect(wrapper.find('.bdm-table').exists()).toBe(false)
    })

    it('shows detail table with budget items in Categorías tab', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Categorías')
      expect(wrapper.text()).toContain('Alimentacion')
      expect(wrapper.text()).toContain('Transporte')
    })

    it('shows Cerrar and Editar presupuesto buttons', () => {
      const wrapper = mountModal({ mode: 'view' })
      const buttons = wrapper.findAll('.btn')
      const texts = buttons.map((b) => b.text())
      expect(texts).toContain('Cerrar')
      expect(texts).toContain('Editar presupuesto')
    })

    it('does not show Configurar presupuestos', () => {
      const wrapper = mountModal({ mode: 'view' })
      expect(wrapper.text()).not.toContain('Configurar presupuestos')
    })

    it('switches to edit mode when Editar presupuesto is clicked', async () => {
      const wrapper = mountModal({ mode: 'view' })
      const editBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Editar presupuesto')
      await editBtn.trigger('click')
      expect(wrapper.find('.bdm-form-list').exists()).toBe(true)
      expect(wrapper.text()).toContain('Edita los montos')
    })

    it('emits close when Cerrar is clicked', async () => {
      const wrapper = mountModal({ mode: 'view' })
      const closeBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Cerrar')
      await closeBtn.trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('Budget Hub tabs', () => {
    it('renders four tabs: Resumen, Categorías, Método, Configuración in view mode', () => {
      const wrapper = mountModal({ mode: 'view' })
      expect(wrapper.find('[role="tablist"]').exists()).toBe(true)
      const labels = wrapper.findAll('[role="tab"]').map((t) => t.text())
      expect(labels).toEqual(['Resumen', 'Categorías', 'Método', 'Configuración'])
    })

    it('switching tabs does not close the modal', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Categorías')
      expect(wrapper.emitted('close')).toBeFalsy()
      expect(wrapper.find('.bdm-modal').exists()).toBe(true)
      await selectTab(wrapper, 'Método')
      await selectTab(wrapper, 'Configuración')
      expect(wrapper.emitted('close')).toBeFalsy()
      expect(wrapper.find('.bdm-modal').exists()).toBe(true)
    })

    it('tab content changes correctly', async () => {
      const wrapper = mountModal({ mode: 'view' })
      expect(wrapper.text()).toContain('Gastado')
      await selectTab(wrapper, 'Categorías')
      expect(wrapper.find('.bdm-table').exists()).toBe(true)
      await selectTab(wrapper, 'Resumen')
      expect(wrapper.find('.bdm-table').exists()).toBe(false)
      expect(wrapper.text()).toContain('Disponible')
    })

    it('edit keeps the active tab context', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Categorías')
      const editBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Editar presupuesto')
      await editBtn.trigger('click')
      expect(wrapper.find('.bdm-form-list').exists()).toBe(true)
      const cancelBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Cancelar')
      await cancelBtn.trigger('click')
      expect(wrapper.find('.bdm-form-list').exists()).toBe(false)
      expect(wrapper.find('.bdm-table').exists()).toBe(true)
    })

    it('ArrowRight moves to the next tab via keyboard', async () => {
      const wrapper = mountModal({ mode: 'view' })
      const tabs = wrapper.findAll('[role="tab"]')
      await tabs[0].trigger('keydown', { key: 'ArrowRight' })
      await new Promise((r) => setTimeout(r, 60))
      await wrapper.vm.$nextTick()
      const updated = wrapper.findAll('[role="tab"]')
      expect(updated[1].attributes('aria-selected')).toBe('true')
      expect(updated[0].attributes('aria-selected')).toBe('false')
    })

    it('ArrowLeft on first tab wraps to the last tab', async () => {
      const wrapper = mountModal({ mode: 'view' })
      const tabs = wrapper.findAll('[role="tab"]')
      await tabs[0].trigger('keydown', { key: 'ArrowLeft' })
      await new Promise((r) => setTimeout(r, 60))
      await wrapper.vm.$nextTick()
      const updated = wrapper.findAll('[role="tab"]')
      expect(updated[3].attributes('aria-selected')).toBe('true')
    })

    it('aria-selected and roving tabindex update on selection', async () => {
      const wrapper = mountModal({ mode: 'view' })
      let tabs = wrapper.findAll('[role="tab"]')
      expect(tabs[0].attributes('aria-selected')).toBe('true')
      expect(tabs[0].attributes('tabindex')).toBe('0')
      expect(tabs[1].attributes('tabindex')).toBe('-1')
      await selectTab(wrapper, 'Método')
      tabs = wrapper.findAll('[role="tab"]')
      expect(tabs[2].attributes('aria-selected')).toBe('true')
      expect(tabs[2].attributes('tabindex')).toBe('0')
      expect(tabs[0].attributes('aria-selected')).toBe('false')
    })

    it('tabs are HIDDEN in create mode and visible in view', () => {
      expect(mountModal({ mode: 'create' }).find('[role="tablist"]').exists()).toBe(false)
      expect(mountModal({ mode: 'view' }).find('[role="tablist"]').exists()).toBe(true)
      expect(mountModal({ mode: 'edit' }).find('[role="tablist"]').exists()).toBe(false)
    })

    it('only one modal exists when navigating', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Categorías')
      await selectTab(wrapper, 'Método')
      await selectTab(wrapper, 'Configuración')
      await selectTab(wrapper, 'Resumen')
      expect(wrapper.findAll('.bdm-modal').length).toBe(1)
    })
  })

  describe('FASE 6.3B — Tab Configuración', () => {
    it('1. shows monthly, income and preferences sections', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Configuración')
      expect(wrapper.text()).toContain('Presupuesto mensual')
      expect(wrapper.text()).toContain('Ingreso de referencia')
      expect(wrapper.text()).toContain('Preferencias')
      expect(wrapper.text()).toContain('Mes activo')
      expect(wrapper.text()).toContain('Última actualización')
    })

    it('shows future income sources as disabled placeholders', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Configuración')
      const options = wrapper.findAll('#income-source option')
      expect(options.length).toBe(4)
      expect(options[0].attributes('disabled')).toBeUndefined()
      expect(options[1].attributes('disabled')).toBeDefined()
      expect(wrapper.text()).toContain('Manual')
    })

    it('shows preference switches with Pronto badge', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Configuración')
      const switches = wrapper.findAll('[role="switch"]')
      expect(switches.length).toBe(2)
      expect(switches[0].attributes('aria-checked')).toBe('false')
      await switches[0].trigger('click')
      expect(switches[0].attributes('aria-checked')).toBe('true')
    })
  })

  describe('FASE 6.3B — Tab Método', () => {
    it('2. catalog shows recommended first, expand shows all 11', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Método')
      const recommended = wrapper.findAll('[data-testid="recommended-methods"] .bdm-method-card')
      expect(recommended.length).toBe(3)
      expect(wrapper.find('[data-testid="show-all-methods"]').exists()).toBe(true)
      await wrapper.find('[data-testid="show-all-methods"]').trigger('click')
      await flush(wrapper)
      const all = wrapper.findAll('[data-testid="all-methods"] .bdm-method-card')
      expect(all.length).toBe(11)
      expect(wrapper.text()).toContain('6 Jarras')
    })

    it('3. selecting a card highlights it and enables Vista previa', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Método')
      expect(wrapper.find('.bdm-method-card.selected').exists()).toBe(false)
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      const selected = wrapper.find('.bdm-method-card.selected')
      expect(selected.exists()).toBe(true)
      expect(selected.attributes('aria-pressed')).toBe('true')
      const previewBtn = wrapper.find('[data-testid="preview-btn"]')
      expect(previewBtn.exists()).toBe(true)
    })

    it('4. preview shows visual amounts without a new modal', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Método')
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      await wrapper.find('#catalog-income').setValue('5000000')
      const previewBtn = wrapper.find('[data-testid="preview-btn"]')
      await previewBtn.trigger('click')
      await flush(wrapper)
      expect(wrapper.find('[data-testid="method-preview"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Así quedaría tu dinero')
      expect(wrapper.text()).toContain('Con un ingreso de referencia de')
      expect(wrapper.findAll('.bdm-modal').length).toBe(1)
      expect(wrapper.text()).toContain('Aplicar método')
      expect(wrapper.text()).toContain('Necesidades')
      expect(wrapper.text()).toContain('$')
    })

    it('5. customization validates the 100% sum visually', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Método')
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      await wrapper.find('#catalog-income').setValue('5000000')
      let previewBtn = wrapper.find('[data-testid="preview-btn"]')
      await previewBtn.trigger('click')
      await flush(wrapper)
      expect(wrapper.text()).toContain('Suma: 100%')
      const personalize = wrapper.findAll('.bdm-link').find((b) => b.text().includes('Personalizar porcentajes'))
      expect(personalize).toBeTruthy()
      await personalize.trigger('click')
      await flush(wrapper)
      const pctInputs = wrapper.findAll('.bdm-form-input--pct')
      await pctInputs[0].setValue('60')
      await flush(wrapper)
      expect(wrapper.text()).toContain('Suma: 110%')
      expect(wrapper.text()).toContain('debe ser 100%')
      const applyBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Aplicar método')
      expect(applyBtn.attributes('disabled')).toBeDefined()
    })

    it('apply saves the method and confirms without touching budgets', async () => {
      methodState.config = null
      const wrapper = mountModal({ mode: 'view' })
      await selectTab(wrapper, 'Método')
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      await wrapper.find('#catalog-income').setValue('5000000')
      const previewBtn = wrapper.find('[data-testid="preview-btn"]')
      await previewBtn.trigger('click')
      await flush(wrapper)
      const applyBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Aplicar método')
      await applyBtn.trigger('click')
      await flush(wrapper)
      expect(methodState.saveConfig).toHaveBeenCalled()
      const saved = methodState.saveConfig.mock.calls[0][0]
      expect(saved.method_type).toBe('50_30_20')
      expect(wrapper.text()).toContain('Método guardado')
      expect(wrapper.text()).toContain('no cambiaron')
      expect(mocks.createBudget).not.toHaveBeenCalled()
      expect(toastMock.success).not.toHaveBeenCalled()
    })
  })

  describe('FASE 6.3B — Grupos en Categorías', () => {
    it('8. shows assigned group and change keeps context', async () => {
      methodState.config = configuredState()
      const wrapper = mountModal({ mode: 'view' })
      await flush(wrapper)
      await selectTab(wrapper, 'Categorías')
      expect(wrapper.text()).toContain('Necesidades')
      const changeBtns = wrapper.findAll('.bdm-link').filter((b) => b.text() === 'Cambiar grupo')
      expect(changeBtns.length).toBeGreaterThan(0)
      await changeBtns[0].trigger('click')
      expect(wrapper.find('.bdm-group-select').exists()).toBe(true)
      await wrapper.find('.bdm-group-select').setValue('gustos')
      const saveBtn = wrapper.findAll('.bdm-link').find((b) => b.text() === 'Guardar')
      await saveBtn.trigger('click')
      await flush(wrapper)
      expect(methodState.saveConfig).toHaveBeenCalled()
      expect(wrapper.find('.bdm-table').exists()).toBe(true)
      expect(wrapper.emitted('close')).toBeFalsy()
      expect(wrapper.text()).toContain('Gustos')
    })
  })

  describe('FASE 6.3B — Onboarding (view mode stepper)', () => {
    it('6. appears on first setup in view mode', async () => {
      const wrapper = mountModal({ mode: 'view' })
      await flush(wrapper)
      expect(wrapper.find('.bdm-onboard').exists()).toBe(true)
      expect(wrapper.text()).toContain('Configurar tu presupuesto')
      expect(wrapper.text()).toContain('Elegir método')
      expect(wrapper.find('[aria-current="step"]').exists()).toBe(true)
    })

    it('7. disappears after completing setup in view mode', async () => {
      methodState.config = configuredState()
      const wrapper = mountModal({ mode: 'view' })
      await flush(wrapper)
      expect(wrapper.find('.bdm-onboard').exists()).toBe(false)
    })
  })

  describe('FASE 6.3C — Hero + Wizard Progress', () => {
    it('opens hero with two clear choices when mode is create', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      expect(wrapper.find('[data-testid="onboard-method"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="onboard-manual"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Configuremos tu presupuesto')
      expect(wrapper.text()).toContain('En menos de un minuto')
      expect(wrapper.text()).toContain('Usar un método')
      expect(wrapper.text()).toContain('Ingresar montos manualmente')
      expect(wrapper.find('.bdm-method-card').exists()).toBe(false)
    })

    it('does not offer Autocompletar con método activo', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      expect(wrapper.text()).not.toContain('Autocompletar')
      expect(wrapper.find('[data-testid="autofill-method"]').exists()).toBe(false)
    })

    it('shows wizard progress bar and hides tabs in create mode', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      expect(wrapper.find('[data-testid="wizard-progress"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Paso 1 de 4')
      expect(wrapper.find('[role="tablist"]').exists()).toBe(false)
    })

    it('shows previous method hint when config exists', async () => {
      methodState.config = configuredState()
      methodState.loadConfig.mockImplementation(async () => configuredState())
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await new Promise((r) => setTimeout(r, 60))
      await wrapper.vm.$nextTick()
      expect(wrapper.find('[data-testid="hero-previous-hint"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Ya usaste')
    })

    it('progress advances to step 2 after choosing method', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      expect(wrapper.text()).toContain('Paso 2 de 4')
      expect(wrapper.text()).toContain('Recomendados')
      const recommended = wrapper.findAll('[data-testid="recommended-methods"] .bdm-method-card')
      expect(recommended.length).toBe(3)
    })

    it('shows only 3 recommended until Ver otros is clicked', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      expect(wrapper.findAll('.bdm-method-card').length).toBe(3)
      expect(wrapper.find('[data-testid="show-all-methods"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Ver otros 8 métodos')
      await wrapper.find('[data-testid="show-all-methods"]').trigger('click')
      await flush(wrapper)
      expect(wrapper.findAll('.bdm-method-card').length).toBe(11)
    })

    it('full flow: hero → catalog → preview visual → apply → grouped categorías → summary', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      await wrapper.find('#catalog-income').setValue('5000000')
      const previewBtn = wrapper.find('[data-testid="preview-btn"]')
      await previewBtn.trigger('click')
      await flush(wrapper)
      expect(wrapper.find('[data-testid="method-preview"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Así quedaría tu dinero')
      const applyBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Aplicar método')
      await applyBtn.trigger('click')
      await flush(wrapper)
      await flush(wrapper)
      expect(wrapper.text()).toContain('Paso 3 de 4')
      expect(wrapper.find('[data-testid="cats-banner"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('¡Listo!')
      expect(toastMock.success).toHaveBeenCalledWith('¡Listo!')
      expect(wrapper.find('[data-testid="group-category-row"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="continue-btn"]').exists()).toBe(true)
      await wrapper.find('[data-testid="continue-btn"]').trigger('click')
      await flush(wrapper)
      expect(wrapper.text()).toContain('Paso 4 de 4')
      expect(wrapper.find('[data-testid="summary-budget-list"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="create-budget-btn"]').exists()).toBe(true)
    })

    it('manual path: hero → form list with back to hero', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await wrapper.find('[data-testid="onboard-manual"]').trigger('click')
      expect(wrapper.find('.bdm-form-list').exists()).toBe(true)
      expect(wrapper.find('[data-testid="wizard-progress"]').exists()).toBe(false)
      await wrapper.find('[data-testid="manual-back"]').trigger('click')
      await flush(wrapper)
      expect(wrapper.find('[data-testid="onboard-method"]').exists()).toBe(true)
    })

    it('has correct modal title for create', () => {
      const wrapper = mountModal({ mode: 'create' })
      expect(wrapper.find('.bdm-title').text()).toContain('Nuevo presupuesto')
    })

    it('loads categories when opened', async () => {
      mountModal({ mode: 'create' })
      await vi.waitFor(() => {
        expect(mocks.loadCategories).toHaveBeenCalled()
      })
    })

    it('shows Cancelar button on hero', () => {
      const wrapper = mountModal({ mode: 'create' })
      const buttons = wrapper.findAll('.btn')
      const texts = buttons.map((b) => b.text())
      expect(texts).toContain('Cancelar')
    })

    it('does not show Configurar presupuestos', () => {
      const wrapper = mountModal({ mode: 'create' })
      expect(wrapper.text()).not.toContain('Configurar presupuesto')
    })

    it('shows error when saving with no amounts in manual mode', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await wrapper.find('[data-testid="onboard-manual"]').trigger('click')
      const saveBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Guardar presupuesto')
      await saveBtn.trigger('click')
      expect(wrapper.find('.bdm-error').exists()).toBe(true)
      expect(wrapper.text()).toContain('Ingresa al menos un monto')
    })

    it('emits close when Cancelar is clicked', async () => {
      const wrapper = mountModal({ mode: 'create' })
      const cancelBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Cancelar')
      await cancelBtn.trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('EDIT mode', () => {
    it('shows edit form with existing budget amounts', () => {
      const wrapper = mountModal({ mode: 'edit' })
      expect(wrapper.find('.bdm-form-list').exists()).toBe(true)
      expect(wrapper.text()).toContain('Alimentacion')
      expect(wrapper.text()).toContain('Transporte')
    })

    it('shows Cancelar and Guardar cambios buttons', () => {
      const wrapper = mountModal({ mode: 'edit' })
      const buttons = wrapper.findAll('.btn')
      const texts = buttons.map((b) => b.text())
      expect(texts).toContain('Cancelar')
      expect(texts).toContain('Guardar cambios')
    })

    it('shows error when saving with no amounts', async () => {
      const wrapper = mountModal({ mode: 'edit' })
      const saveBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Guardar cambios')
      await saveBtn.trigger('click')
      expect(wrapper.find('.bdm-error').exists()).toBe(true)
      expect(wrapper.text()).toContain('No hay cambios')
    })

    it('returns to view mode when Cancelar is clicked', async () => {
      const wrapper = mountModal({ mode: 'edit' })
      const cancelBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Cancelar')
      await cancelBtn.trigger('click')
      expect(wrapper.find('.bdm-form-list').exists()).toBe(false)
      expect(wrapper.text()).toContain('Gastado')
    })

    it('has correct modal title for edit', () => {
      const wrapper = mountModal({ mode: 'edit' })
      expect(wrapper.find('.bdm-title').text()).toContain('Editar presupuesto')
    })
  })

  describe('Accessibility', () => {
    it('has aria-modal and role=dialog', () => {
      const wrapper = mountModal()
      const modal = wrapper.find('.bdm-modal')
      expect(modal.attributes('aria-modal')).toBe('true')
      expect(modal.attributes('role')).toBe('dialog')
    })

    it('has correct aria-label per mode', () => {
      expect(mountModal({ mode: 'create' }).find('.bdm-modal').attributes('aria-label')).toContain('Nuevo')
      expect(mountModal({ mode: 'edit' }).find('.bdm-modal').attributes('aria-label')).toContain('Editar')
      expect(mountModal({ mode: 'view' }).find('.bdm-modal').attributes('aria-label')).toContain('detallado')
    })

    it('has aria-live assertive on error messages', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await wrapper.find('[data-testid="onboard-manual"]').trigger('click')
      const saveBtn = wrapper.findAll('.btn').find((b) => b.text() === 'Guardar presupuesto')
      await saveBtn.trigger('click')
      const error = wrapper.find('.bdm-error')
      expect(error.attributes('role')).toBe('alert')
      expect(error.attributes('aria-live')).toBe('assertive')
    })

    it('inputs have associated labels via for/id in manual mode', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await wrapper.find('[data-testid="onboard-manual"]').trigger('click')
      const labels = wrapper.findAll('label.bdm-form-label')
      const inputs = wrapper.findAll('.bdm-form-input')
      expect(labels.length).toBe(inputs.length)
      labels.forEach((label) => {
        const forAttr = label.attributes('for')
        expect(forAttr).toBeTruthy()
        expect(wrapper.find(`#${forAttr}`).exists()).toBe(true)
      })
    })

    it('wizard progress has role=progressbar with aria values', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      const bar = wrapper.find('[data-testid="wizard-progress"]')
      expect(bar.attributes('role')).toBe('progressbar')
      expect(bar.attributes('aria-valuenow')).toBe('25')
      expect(bar.attributes('aria-valuemin')).toBe('0')
      expect(bar.attributes('aria-valuemax')).toBe('100')
    })
  })

  describe('Keyboard', () => {
    it('closes on Escape key via document listener', async () => {
      const wrapper = mountModal()
      const event = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
      document.dispatchEvent(event)
      await wrapper.vm.$nextTick()
      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('9. tabs keep keyboard navigation with four tabs in view', async () => {
      const wrapper = mountModal({ mode: 'view' })
      const tabs = wrapper.findAll('[role="tab"]')
      expect(tabs.length).toBe(4)
      await tabs[3].trigger('keydown', { key: 'ArrowRight' })
      await new Promise((r) => setTimeout(r, 60))
      await wrapper.vm.$nextTick()
      const updated = wrapper.findAll('[role="tab"]')
      expect(updated[0].attributes('aria-selected')).toBe('true')
      await updated[0].trigger('keydown', { key: 'End' })
      await new Promise((r) => setTimeout(r, 60))
      await wrapper.vm.$nextTick()
      const final = wrapper.findAll('[role="tab"]')
      expect(final[3].attributes('aria-selected')).toBe('true')
    })
  })

  describe('FASE 6.3B-HF1 — Onboarding Integration', () => {
    it('opens hero when "Crear presupuesto" is clicked from Resumen', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      expect(wrapper.find('[data-testid="onboard-method"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Configuremos tu presupuesto')
      expect(wrapper.find('.bdm-method-card').exists()).toBe(false)
    })

    it('user never leaves BudgetDetailModal during onboarding', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      expect(wrapper.findAll('.bdm-modal').length).toBe(1)
    })
  })

  describe('FASE 6.3C-HF3 — Wizard continuity', () => {
    it('hides income and preview CTA until a method is selected', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      expect(wrapper.find('[data-testid="income-section"]').exists()).toBe(false)
      expect(wrapper.find('[data-testid="selection-callout"]').exists()).toBe(false)
      expect(wrapper.find('[data-testid="preview-btn"]').exists()).toBe(false)
    })

    it('shows callout, income and preview CTA after selecting a method', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      await flush(wrapper)
      expect(wrapper.find('[data-testid="income-section"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="selection-callout"]').text()).toBe(
        'Perfecto. Ahora ingresa cuánto recibes al mes.',
      )
      expect(wrapper.find('[data-testid="preview-btn"]').exists()).toBe(true)
      expect(wrapper.find('.bmt-preview-cta-title').text()).toBe('Vista previa')
      expect(wrapper.find('.bmt-preview-cta-sub').text()).toBe(
        'Mira cómo se distribuiría tu ingreso antes de aplicarlo.',
      )
      expect(wrapper.find('[data-testid="preview-btn"]').text()).toContain(
        'Ver cómo quedaría mi dinero',
      )
    })

    it('selecting a method scrolls to income section without breaking in jsdom', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      const card = wrapper.findAll('.bdm-method-card')[0]
      await card.trigger('click')
      await flush(wrapper)
      expect(wrapper.find('[data-testid="income-section"]').exists()).toBe(true)
      expect(wrapper.find('.bdm-method-card.selected').exists()).toBe(true)
    })

    it('shows categories banner with exact copy only in create wizard', async () => {
      methodState.config = configuredState()
      const viewWrapper = mountModal({ mode: 'view' })
      await flush(viewWrapper)
      await selectTab(viewWrapper, 'Categorías')
      expect(viewWrapper.find('[data-testid="cats-banner"]').exists()).toBe(false)

      methodState.config = null
      const createWrapper = mountModal({ mode: 'create' })
      await flush(createWrapper)
      await goToCatalog(createWrapper)
      await createWrapper.findAll('.bdm-method-card')[0].trigger('click')
      await createWrapper.find('#catalog-income').setValue('5000000')
      await createWrapper.find('[data-testid="preview-btn"]').trigger('click')
      await flush(createWrapper)
      await createWrapper.find('[data-testid="apply-method"]').trigger('click')
      await flush(createWrapper)
      await flush(createWrapper)
      expect(createWrapper.find('[data-testid="cats-banner"]').exists()).toBe(true)
      expect(createWrapper.find('[data-testid="cats-banner"]').text()).toContain(
        '¡Listo! Distribuimos tu ingreso. Ahora asignemos las categorías.',
      )
    })

    it('apply method navigates to Categorías (Paso 3 de 4) and fires toast', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      await wrapper.find('#catalog-income').setValue('5000000')
      await wrapper.find('[data-testid="preview-btn"]').trigger('click')
      await flush(wrapper)
      await wrapper.find('[data-testid="apply-method"]').trigger('click')
      await flush(wrapper)
      await flush(wrapper)
      expect(wrapper.text()).toContain('Paso 3 de 4')
      expect(wrapper.find('[data-testid="group-category-row"]').exists()).toBe(true)
      expect(toastMock.success).toHaveBeenCalledWith('¡Listo!')
    })

    it('preview CTA button is full-width primary with Sparkles icon mock', async () => {
      const wrapper = mountModal({ mode: 'create' })
      await flush(wrapper)
      await goToCatalog(wrapper)
      await wrapper.findAll('.bdm-method-card')[0].trigger('click')
      await flush(wrapper)
      const btn = wrapper.find('[data-testid="preview-btn"]')
      expect(btn.classes()).toContain('btn-primary')
      expect(btn.classes()).toContain('bmt-preview-cta-btn')
      expect(btn.text()).toContain('Ver cómo quedaría mi dinero')
    })
  })
})

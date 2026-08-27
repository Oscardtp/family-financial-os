<template>
  <div class="patrimony-page">
    <div class="page-header">
      <h2 class="page-title">Patrimonio</h2>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <span>Cargando patrimonio...</span>
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-sm" @click="loadData">Reintentar</button>
    </div>

    <template v-else>
      <div class="summary-cards">
        <div class="summary-card assets">
          <span class="summary-label">Total Activos</span>
          <span class="summary-value income">${{ fmt(totalAssets) }}</span>
        </div>
        <div class="summary-card liabilities">
          <span class="summary-label">Total Pasivos</span>
          <span class="summary-value expense">${{ fmt(totalLiabilities) }}</span>
        </div>
        <div class="summary-card net">
          <span class="summary-label">Patrimonio Neto</span>
          <span class="summary-value" :class="netPatrimony >= 0 ? 'income' : 'expense'">${{ fmt(netPatrimony) }}</span>
        </div>
      </div>

      <div class="card" style="margin-bottom: var(--spacing-md);">
        <h3 class="card-title">Activos vs Pasivos</h3>
        <ChartCard type="bar" :data="chartData" :options="{ indexAxis: 'y', scales: { x: { beginAtZero: true } } }" />
      </div>

      <div class="patrimony-grid">
        <PatrimonyItemList
          title="Activos"
          :items="assets"
          :value-accessor="a => a.value"
          value-class="income"
          empty-text="No hay activos registrados"
          @edit="openEditAsset"
          @delete="deleteAsset"
        />
        <PatrimonyItemList
          title="Pasivos"
          :items="liabilities"
          :value-accessor="l => l.current_balance"
          value-class="expense"
          empty-text="No hay pasivos registrados"
          @edit="openEditLiability"
          @delete="deleteLiability"
        />
      </div>

      <div class="forms-row">
        <PatrimonyItemForm
          title="Nuevo Activo"
          type-label="activo"
          :fields="['name', 'type', 'value', 'purchase_date']"
          :type-options="assetTypes"
          submit-label="Crear Activo"
          @submit="createAsset"
        />
        <PatrimonyItemForm
          title="Nuevo Pasivo"
          type-label="pasivo"
          :fields="['name', 'type', 'total_amount', 'current_balance', 'interest_rate', 'monthly_payment']"
          :type-options="liabilityTypes"
          submit-label="Crear Pasivo"
          @submit="createLiability"
        />
      </div>
    </template>

    <PatrimonyEditModal
      :show="showEditAssetModal"
      title="Editar Activo"
      :item="editAssetData"
      :type-options="assetTypes"
      value-label="Valor"
      @close="showEditAssetModal = false"
      @saved="saveAsset"
    />

    <PatrimonyEditModal
      :show="showEditLiabilityModal"
      title="Editar Pasivo"
      :item="editLiabilityData"
      :type-options="liabilityTypes"
      value-label="Saldo Actual"
      @close="showEditLiabilityModal = false"
      @saved="saveLiability"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useCurrency } from '@/composables/useCurrency'
import ChartCard from '@/components/ChartCard.vue'
import PatrimonyItemList from '@/components/patrimony/PatrimonyItemList.vue'
import PatrimonyItemForm from '@/components/patrimony/PatrimonyItemForm.vue'
import PatrimonyEditModal from '@/components/patrimony/PatrimonyEditModal.vue'

const { fmt } = useCurrency()

const assets = ref([])
const liabilities = ref([])
const loading = ref(true)
const error = ref('')

const showEditAssetModal = ref(false)
const editAssetData = ref(null)
const showEditLiabilityModal = ref(false)
const editLiabilityData = ref(null)

const assetTypes = [
  { value: 'inmueble', label: 'Inmueble' },
  { value: 'vehiculo', label: 'Vehículo' },
  { value: 'inversion', label: 'Inversión' },
  { value: 'ahorro', label: 'Ahorro' },
  { value: 'otro', label: 'Otro' },
]

const liabilityTypes = [
  { value: 'hipoteca', label: 'Hipoteca' },
  { value: 'prestamo', label: 'Préstamo' },
  { value: 'tarjeta_credito', label: 'Tarjeta de Crédito' },
  { value: 'prestamo_estudiantil', label: 'Préstamo Estudiantil' },
  { value: 'otro', label: 'Otro' },
]

const totalAssets = computed(() => assets.value.reduce((s, a) => s + (a.value || 0), 0))
const totalLiabilities = computed(() => liabilities.value.reduce((s, l) => s + (l.current_balance || 0), 0))
const netPatrimony = computed(() => totalAssets.value - totalLiabilities.value)

const chartData = computed(() => ({
  labels: ['Activos', 'Pasivos'],
  datasets: [{
    data: [totalAssets.value, totalLiabilities.value],
    backgroundColor: ['#16a34a', '#dc2626'],
    borderRadius: 4,
  }],
}))

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [assetsRes, liabilitiesRes] = await Promise.all([
      api.get('/patrimony/assets'),
      api.get('/patrimony/liabilities'),
    ])
    assets.value = assetsRes.data
    liabilities.value = liabilitiesRes.data
  } catch {
    error.value = 'Error al cargar el patrimonio'
  } finally {
    loading.value = false
  }
}

async function createAsset(payload) {
  if (!payload.purchase_date) delete payload.purchase_date
  const { data } = await api.post('/patrimony/assets', payload)
  assets.value.push(data)
}

async function createLiability(payload) {
  const { data } = await api.post('/patrimony/liabilities', payload)
  liabilities.value.push(data)
}

function openEditAsset(asset) {
  editAssetData.value = asset
  showEditAssetModal.value = true
}

async function saveAsset(payload) {
  const { data } = await api.put(`/patrimony/assets/${editAssetData.value.id}`, payload)
  const idx = assets.value.findIndex(a => a.id === editAssetData.value.id)
  if (idx !== -1) assets.value[idx] = data
  showEditAssetModal.value = false
}

async function deleteAsset(id) {
  if (!confirm('¿Eliminar este activo?')) return
  await api.delete(`/patrimony/assets/${id}`)
  assets.value = assets.value.filter(a => a.id !== id)
}

function openEditLiability(liability) {
  editLiabilityData.value = liability
  showEditLiabilityModal.value = true
}

async function saveLiability(payload) {
  const { data } = await api.put(`/patrimony/liabilities/${editLiabilityData.value.id}`, payload)
  const idx = liabilities.value.findIndex(l => l.id === editLiabilityData.value.id)
  if (idx !== -1) liabilities.value[idx] = data
  showEditLiabilityModal.value = false
}

async function deleteLiability(id) {
  if (!confirm('¿Eliminar este pasivo?')) return
  await api.delete(`/patrimony/liabilities/${id}`)
  liabilities.value = liabilities.value.filter(l => l.id !== id)
}

onMounted(loadData)
</script>

<style scoped>
.patrimony-page { max-width: 960px; margin: 0 auto; }
.page-header { margin-bottom: var(--spacing-xl); }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-neutral-900); }
.spinner {
  width: 24px; height: 24px; border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-600); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.summary-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md); margin-bottom: var(--spacing-xl); }
.summary-card {
  background: var(--color-neutral-0); border-radius: var(--radius-lg);
  padding: var(--spacing-lg); text-align: center; box-shadow: var(--shadow-sm);
  border-top: 3px solid;
}
.summary-card.assets { border-color: var(--color-success-500); }
.summary-card.liabilities { border-color: var(--color-error-500); }
.summary-card.net { border-color: var(--color-primary-500); }
.summary-label { display: block; font-size: 0.75rem; color: var(--color-neutral-500); margin-bottom: 4px; }
.summary-value { display: block; font-size: 1.25rem; font-weight: 700; font-family: var(--font-mono); }
.summary-value.income { color: var(--color-success-600); }
.summary-value.expense { color: var(--color-error-600); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--spacing-md); }
.patrimony-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); margin-bottom: var(--spacing-xl); }
.forms-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); margin-bottom: var(--spacing-xl); }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); background: var(--color-neutral-100); color: var(--color-neutral-700); }

@media (max-width: 768px) {
  .summary-cards { grid-template-columns: 1fr; }
  .patrimony-grid, .forms-row { grid-template-columns: 1fr; }
}
</style>

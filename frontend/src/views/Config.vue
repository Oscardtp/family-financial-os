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
      <div class="config-section card">
        <h3 class="section-title">Tu perfil</h3>
        <div class="config-row">
          <span class="config-label">Nombre</span>
          <span class="config-value">{{ user?.name || 'Sin nombre' }}</span>
        </div>
        <div class="config-row">
          <span class="config-label">Email</span>
          <span class="config-value">{{ user?.email || 'Sin email' }}</span>
        </div>
      </div>

      <div class="config-section card">
        <h3 class="section-title">Hogar</h3>
        <div class="config-row">
          <span class="config-label">Tu familia</span>
          <router-link to="/household" class="config-link">Ver miembros</router-link>
        </div>
      </div>

      <div class="config-section card">
        <h3 class="section-title">Datos</h3>
        <div class="config-row">
          <span class="config-label">Exportar movimientos</span>
          <button class="btn btn-sm btn-outline" @click="exportCSV" :disabled="exporting">
            {{ exporting ? 'Descargando...' : 'Descargar CSV' }}
          </button>
        </div>
      </div>

      <div class="config-section card">
        <h3 class="section-title">Sesión</h3>
        <button class="btn btn-sm btn-danger" @click="handleLogout">Cerrar sesión</button>
      </div>
    </template>

    <template v-else-if="activeTab === 'categories'">
      <div v-if="catLoading" class="loading-state">
        <SkeletonLoader v-for="n in 4" :key="n" variant="card" />
      </div>

      <template v-else>
        <div class="categories-grid">
          <div v-for="cat in categories" :key="cat.id" class="category-card">
            <div class="category-icon" :style="{ background: cat.color || 'var(--color-neutral-200)' }">
              {{ cat.icon || cat.name.charAt(0) }}
            </div>
            <div class="category-info">
              <span class="category-name">{{ cat.name }}</span>
              <span class="category-type-badge" :class="'type-' + cat.type">
                {{ cat.type === 'income' ? 'Ingreso' : 'Gasto' }}
              </span>
            </div>
            <button class="btn-icon-danger" @click="confirmDeleteCategory(cat.id)" aria-label="Eliminar categoría">
              <X :size="14" />
            </button>
          </div>

          <div v-if="!categories.length" class="empty-state">
            <p>No tienes categorías creadas</p>
          </div>
        </div>

        <div class="card form-card">
          <h3 class="section-title">Nueva categoría</h3>
          <form class="form" @submit.prevent="createCategory">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Nombre</label>
                <input v-model="catForm.name" class="form-input" type="text" required placeholder="Nombre de la categoría" />
              </div>
              <div class="form-group">
                <label class="form-label">Tipo</label>
                <select v-model="catForm.type" class="form-select" required>
                  <option value="income">Ingreso</option>
                  <option value="expense">Gasto</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Icono (opcional)</label>
                <input v-model="catForm.icon" class="form-input" type="text" placeholder="Emoji o texto" />
              </div>
              <div class="form-group">
                <label class="form-label">Color (opcional)</label>
                <input v-model="catForm.color" class="form-input" type="color" />
              </div>
            </div>
            <div class="form-actions">
              <span v-if="catFormError" class="form-error">{{ catFormError }}</span>
              <button class="btn btn-primary" type="submit" :disabled="catSubmitting">
                {{ catSubmitting ? 'Creando...' : 'Crear categoría' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </template>

    <template v-else-if="activeTab === 'accounts'">
      <div v-if="accLoading" class="loading-state">
        <SkeletonLoader v-for="n in 3" :key="n" variant="card" />
      </div>

      <template v-else>
        <div class="accounts-grid">
          <div v-for="account in accounts" :key="account.id" class="account-card">
            <div class="account-icon" :style="{ background: iconBg(account.type), color: iconColor(account.type) }">
              <component :is="iconMap[account.type]" :size="20" />
            </div>
            <div class="account-body">
              <span class="account-name">{{ account.name }}</span>
              <span class="account-type">{{ typeLabels[account.type] || account.type }}</span>
            </div>
            <div class="account-balance">
              <span class="account-currency">{{ account.currency || 'COP' }}</span>
              <span class="account-amount">{{ fmtAcc(account.balance) }}</span>
            </div>
            <div class="account-actions">
              <button class="btn-icon-danger" @click="confirmDeleteAccount(account.id)" aria-label="Eliminar cuenta">
                <X :size="14" />
              </button>
            </div>
          </div>

          <div v-if="!accounts.length" class="empty-state">
            <p>No tienes cuentas creadas</p>
          </div>
        </div>

        <div class="card form-card">
          <h3 class="section-title">Nueva cuenta</h3>
          <form class="form" @submit.prevent="createAccount">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Nombre</label>
                <input v-model="accForm.name" class="form-input" type="text" required placeholder="Nombre de la cuenta" />
              </div>
              <div class="form-group">
                <label class="form-label">Tipo</label>
                <select v-model="accForm.type" class="form-select" required>
                  <option value="cash">Efectivo</option>
                  <option value="bank">Banco</option>
                  <option value="wallet">Billetera</option>
                  <option value="credit_card">Tarjeta de crédito</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Saldo inicial</label>
                <input v-model.number="accForm.balance" class="form-input" type="number" step="0.01" required />
              </div>
            </div>
            <div class="form-actions">
              <span v-if="accFormError" class="form-error">{{ accFormError }}</span>
              <button class="btn btn-primary" type="submit" :disabled="accSubmitting">
                {{ accSubmitting ? 'Creando...' : 'Crear cuenta' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </template>

    <ConfirmDialog
      :open="showCatConfirm"
      title="Eliminar categoría"
      message="¿Seguro que quieres eliminar esta categoría? Se perderán todos los datos asociados."
      confirm-text="Eliminar"
      cancel-text="Cancelar"
      variant="danger"
      @confirm="handleDeleteCategoryConfirm"
      @cancel="showCatConfirm = false"
    />

    <ConfirmDialog
      :open="showAccConfirm"
      title="Eliminar cuenta"
      message="¿Seguro que quieres eliminar esta cuenta? Se perderán todos los datos asociados."
      confirm-text="Eliminar"
      cancel-text="Cancelar"
      variant="danger"
      @confirm="handleDeleteAccountConfirm"
      @cancel="showAccConfirm = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Tag, Wallet, Banknote, CreditCard, PiggyBank, X } from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { useCurrency } from '@/composables/useCurrency'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { fmt: fmtAcc } = useCurrency()
const toast = useToast()
const user = computed(() => auth.user)

const tabs = [
  { key: 'profile', label: 'Perfil', icon: User },
  { key: 'categories', label: 'Categorías', icon: Tag },
  { key: 'accounts', label: 'Cuentas', icon: Wallet },
]

const activeTab = ref(route.query.tab || 'profile')
watch(() => route.query.tab, (t) => { if (t) activeTab.value = t })

const exporting = ref(false)

async function exportCSV() {
  exporting.value = true
  try {
    const response = await api.get('/reports/transactions/csv', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'movimientos.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    toast.success('Descarga completada')
  } catch {
    toast.error('No pudimos descargar. Intenta de nuevo.')
  } finally {
    exporting.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

const categories = ref([])
const catLoading = ref(true)
const catSubmitting = ref(false)
const catFormError = ref('')
const catForm = reactive({ name: '', type: 'expense', icon: '', color: '#6366f1' })

const catToDelete = ref(null)
const showCatConfirm = ref(false)

function confirmDeleteCategory(id) {
  catToDelete.value = id
  showCatConfirm.value = true
}

async function handleDeleteCategoryConfirm() {
  if (!catToDelete.value) return
  try {
    await api.delete(`/categories/${catToDelete.value}`)
    categories.value = categories.value.filter(c => c.id !== catToDelete.value)
    toast.success('Categoría eliminada')
  } catch {
    toast.error('No pudimos eliminar la categoría')
  } finally {
    showCatConfirm.value = false
    catToDelete.value = null
  }
}

async function loadCategories() {
  catLoading.value = true
  try {
    const { data } = await api.get('/categories')
    categories.value = data
  } catch {
    toast.error('No pudimos cargar las categorías')
  } finally {
    catLoading.value = false
  }
}

async function createCategory() {
  catSubmitting.value = true
  catFormError.value = ''
  try {
    const payload = { name: catForm.name, type: catForm.type }
    if (catForm.icon) payload.icon = catForm.icon
    if (catForm.color) payload.color = catForm.color
    const { data } = await api.post('/categories', payload)
    categories.value.push(data)
    catForm.name = ''
    catForm.type = 'expense'
    catForm.icon = ''
    catForm.color = '#6366f1'
    toast.success('Categoría creada')
  } catch (e) {
    catFormError.value = e.response?.data?.detail || 'No pudimos crear la categoría'
  } finally {
    catSubmitting.value = false
  }
}

const accounts = ref([])
const accLoading = ref(true)
const accSubmitting = ref(false)
const accFormError = ref('')
const accForm = reactive({ name: '', type: 'cash', balance: 0, currency: 'COP' })

const accToDelete = ref(null)
const showAccConfirm = ref(false)

function confirmDeleteAccount(id) {
  accToDelete.value = id
  showAccConfirm.value = true
}

async function handleDeleteAccountConfirm() {
  if (!accToDelete.value) return
  try {
    await api.delete(`/accounts/${accToDelete.value}`)
    accounts.value = accounts.value.filter(a => a.id !== accToDelete.value)
    toast.success('Cuenta eliminada')
  } catch {
    toast.error('No pudimos eliminar la cuenta')
  } finally {
    showAccConfirm.value = false
    accToDelete.value = null
  }
}

const iconMap = { cash: Banknote, bank: Wallet, wallet: PiggyBank, credit_card: CreditCard }
const typeLabels = { cash: 'Efectivo', bank: 'Banco', wallet: 'Billetera', credit_card: 'Tarjeta de crédito' }

function iconBg(type) {
  const map = { cash: 'var(--color-success-100)', bank: 'var(--color-primary-100)', wallet: 'var(--color-warning-100)', credit_card: 'var(--color-error-100)' }
  return map[type] || 'var(--color-neutral-100)'
}
function iconColor(type) {
  const map = { cash: 'var(--color-success-600)', bank: 'var(--color-primary-600)', wallet: 'var(--color-warning-600)', credit_card: 'var(--color-error-600)' }
  return map[type] || 'var(--color-neutral-600)'
}

async function loadAccounts() {
  accLoading.value = true
  try {
    const { data } = await api.get('/accounts')
    accounts.value = data
  } catch {
    toast.error('No pudimos cargar las cuentas')
  } finally {
    accLoading.value = false
  }
}

async function createAccount() {
  accSubmitting.value = true
  accFormError.value = ''
  try {
    const { data } = await api.post('/accounts', { ...accForm })
    accounts.value.push(data)
    accForm.name = ''
    accForm.type = 'cash'
    accForm.balance = 0
    toast.success('Cuenta creada')
  } catch (e) {
    accFormError.value = e.response?.data?.detail || 'No pudimos crear la cuenta'
  } finally {
    accSubmitting.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'categories') loadCategories()
  if (tab === 'accounts') loadAccounts()
})

onMounted(() => {
  if (activeTab.value === 'categories') loadCategories()
  if (activeTab.value === 'accounts') loadAccounts()
})
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

.config-section { margin-bottom: var(--spacing-md); }
.section-title { font-size: 0.9rem; font-weight: 600; color: var(--color-neutral-700); margin-bottom: var(--spacing-md); }
.config-row { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--color-neutral-100); }
.config-row:last-child { border-bottom: none; }
.config-label { font-size: 0.875rem; color: var(--color-neutral-600); }
.config-value { font-size: 0.875rem; color: var(--color-neutral-900); font-weight: 500; }
.config-link { font-size: 0.85rem; color: var(--color-primary-600); text-decoration: none; font-weight: 500; }
.config-link:hover { text-decoration: underline; }

.categories-grid, .accounts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg); }
.category-card, .account-card {
  background: var(--color-neutral-0); border-radius: var(--radius-lg); padding: var(--spacing-md);
  box-shadow: var(--shadow-sm); display: flex; align-items: center; gap: var(--spacing-md);
  border: 1px solid var(--color-neutral-100);
}
.category-icon {
  width: 40px; height: 40px; border-radius: var(--radius-md); display: flex;
  align-items: center; justify-content: center; flex-shrink: 0; font-size: 1.1rem; color: white;
}
.category-info, .account-body { flex: 1; min-width: 0; }
.category-name, .account-name { display: block; font-weight: 600; font-size: 0.85rem; color: var(--color-neutral-900); }
.account-type { display: block; font-size: 0.75rem; color: var(--color-neutral-400); margin-top: 2px; }
.category-type-badge {
  display: inline-block; font-size: 0.7rem; font-weight: 500; padding: 2px 8px;
  border-radius: var(--radius-full); margin-top: 4px;
}
.type-income { background: var(--color-success-100); color: var(--color-success-700); }
.type-expense { background: var(--color-error-100); color: var(--color-error-700); }

.account-icon {
  width: 40px; height: 40px; border-radius: var(--radius-md); display: flex;
  align-items: center; justify-content: center; flex-shrink: 0;
}
.account-balance { text-align: right; flex-shrink: 0; }
.account-currency { display: block; font-size: 0.7rem; color: var(--color-neutral-400); }
.account-amount { display: block; font-weight: 700; font-size: 0.9rem; color: var(--color-neutral-900); font-family: var(--font-mono); }
.account-actions { flex-shrink: 0; }

.btn-icon-danger {
  background: none; border: none; color: var(--color-neutral-400); cursor: pointer;
  padding: 4px; border-radius: var(--radius-sm); transition: all var(--transition-fast);
}
.btn-icon-danger:hover { color: var(--color-error-500); background: var(--color-error-50); }

.form-card { margin-bottom: var(--spacing-md); }
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.form-label { font-size: 0.8rem; font-weight: 500; color: var(--color-neutral-700); }
.form-input, .form-select {
  padding: var(--spacing-sm) var(--spacing-md); border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md); font-size: 0.875rem; color: var(--color-neutral-900);
  background: var(--color-neutral-0); outline: none; transition: border-color var(--transition-fast);
}
.form-input:focus, .form-select:focus { border-color: var(--color-primary-500); }
.form-actions { display: flex; align-items: center; justify-content: flex-end; gap: var(--spacing-md); margin-top: var(--spacing-sm); }
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn { padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; transition: background var(--transition-fast); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }
.btn-primary { background: var(--color-primary-600); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }
.btn-outline { background: var(--color-neutral-0); border: 1px solid var(--color-neutral-200); color: var(--color-neutral-700); }
.btn-outline:hover { border-color: var(--color-primary-400); color: var(--color-primary-600); }
.btn-danger { background: var(--color-error-600); color: white; }
.btn-danger:hover { background: var(--color-error-700); }

.empty-state { grid-column: 1 / -1; text-align: center; padding: var(--spacing-2xl); color: var(--color-neutral-400); font-size: 0.875rem; }
.loading-state { display: flex; flex-direction: column; gap: var(--spacing-md); }

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
  .categories-grid, .accounts-grid { grid-template-columns: 1fr; }
  .config-tabs { overflow-x: auto; }
}
</style>

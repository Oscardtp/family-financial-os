<template>
  <div class="accounts-page">
    <div class="page-header">
      <h2 class="page-title">
        Cuentas
      </h2>
    </div>

    <div
      v-if="loading"
      class="loading-state"
    >
      <div class="accounts-grid">
        <SkeletonLoader
          v-for="n in 4"
          :key="n"
          variant="card"
        />
      </div>
    </div>

    <div
      v-else-if="error"
      class="error-state"
    >
      <span>{{ error }}</span>
      <button
        class="btn btn-sm"
        @click="loadAccounts"
      >
        Reintentar
      </button>
    </div>

    <template v-else>
      <div class="accounts-grid">
        <div
          v-for="account in accounts"
          :key="account.id"
          class="account-card card-hover"
        >
          <div
            class="account-icon"
            :style="{ background: iconBg(account.type), color: iconColor(account.type) }"
          >
            <component
              :is="iconMap[account.type]"
              :size="20"
            />
          </div>
          <div class="account-body">
            <span class="account-name">{{ account.name }}</span>
            <span class="account-type">{{ typeLabels[account.type] || account.type }}</span>
          </div>
          <div class="account-balance">
            <span class="account-currency">{{ account.currency || 'COP' }}</span>
            <span class="account-amount">{{ fmt(account.balance) }}</span>
          </div>
          <div class="account-actions">
            <button
              class="btn btn-sm btn-outline"
              @click="openEdit(account)"
            >
              Editar
            </button>
            <button
              class="btn btn-sm btn-danger"
              @click="deleteAccount(account.id)"
            >
              Eliminar
            </button>
          </div>
        </div>

        <div
          v-if="!accounts.length"
          class="empty-state"
        >
          <p>No hay cuentas registradas</p>
        </div>
      </div>

      <div
        v-if="showEditModal"
        class="modal-overlay"
        @click.self="showEditModal = false"
      >
        <div class="modal">
          <h3 class="modal-title">
            Editar Cuenta
          </h3>
          <form
            class="form"
            @submit.prevent="editAccount"
          >
            <div class="form-group">
              <label class="form-label">Nombre</label>
              <input
                v-model="editForm.name"
                class="form-input"
                type="text"
                required
              >
            </div>
            <div class="form-group">
              <label class="form-label">Tipo</label>
              <select
                v-model="editForm.type"
                class="form-select"
                required
              >
                <option value="cash">
                  Efectivo
                </option>
                <option value="bank">
                  Banco
                </option>
                <option value="wallet">
                  Billetera
                </option>
                <option value="credit_card">
                  Tarjeta de Credito
                </option>
              </select>
            </div>
            <div class="form-actions">
              <span
                v-if="editError"
                class="form-error"
              >{{ editError }}</span>
              <button
                class="btn btn-sm"
                type="button"
                @click="showEditModal = false"
              >
                Cancelar
              </button>
              <button
                class="btn btn-primary"
                type="submit"
                :disabled="editing"
              >
                {{ editing ? 'Guardando...' : 'Guardar' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="card form-card card-hover">
        <h3 class="card-title">
          Nueva Cuenta
        </h3>
        <form
          class="form"
          @submit.prevent="createAccount"
        >
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nombre</label>
              <input
                v-model="form.name"
                class="form-input"
                type="text"
                required
                placeholder="Nombre de la cuenta"
              >
            </div>
            <div class="form-group">
              <label class="form-label">Tipo</label>
              <select
                v-model="form.type"
                class="form-select"
                required
              >
                <option value="cash">
                  Efectivo
                </option>
                <option value="bank">
                  Banco
                </option>
                <option value="wallet">
                  Billetera
                </option>
                <option value="credit_card">
                  Tarjeta de Credito
                </option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Saldo Inicial</label>
              <input
                v-model.number="form.balance"
                class="form-input"
                type="number"
                step="0.01"
                required
              >
            </div>
          </div>
          <div class="form-actions">
            <span
              v-if="formError"
              class="form-error"
            >{{ formError }}</span>
            <button
              class="btn btn-primary"
              type="submit"
              :disabled="submitting"
            >
              {{ submitting ? 'Creando...' : 'Crear Cuenta' }}
            </button>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Wallet, Landmark, Smartphone, CreditCard } from 'lucide-vue-next'
import api from '@/services/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const accounts = ref([])
const loading = ref(true)
const error = ref('')
const submitting = ref(false)
const formError = ref('')
const showEditModal = ref(false)
const editError = ref('')
const editing = ref(false)
const editingId = ref(null)

const form = reactive({
  name: '',
  type: 'cash',
  balance: 0,
  currency: 'COP',
})

const editForm = reactive({
  name: '',
  type: 'cash',
})

const typeLabels = {
  cash: 'Efectivo',
  bank: 'Banco',
  wallet: 'Billetera',
  credit_card: 'Tarjeta de Credito',
}

const iconMap = {
  cash: Wallet,
  bank: Landmark,
  wallet: Smartphone,
  credit_card: CreditCard,
}

function iconBg(type) {
  const map = {
    cash: 'var(--color-success-100)',
    bank: 'var(--color-primary-100)',
    wallet: 'var(--color-warning-100)',
    credit_card: 'var(--color-error-100)',
  }
  return map[type] || 'var(--color-neutral-100)'
}

function iconColor(type) {
  const map = {
    cash: 'var(--color-success-600)',
    bank: 'var(--color-primary-600)',
    wallet: 'var(--color-warning-600)',
    credit_card: 'var(--color-error-600)',
  }
  return map[type] || 'var(--color-neutral-600)'
}

async function loadAccounts() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/accounts')
    accounts.value = data
  } catch (e) {
    error.value = 'Error al cargar las cuentas'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function createAccount() {
  submitting.value = true
  formError.value = ''
  try {
    const { data } = await api.post('/accounts', { ...form })
    accounts.value.push(data)
    form.name = ''
    form.type = 'cash'
    form.balance = 0
    form.currency = 'COP'
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Error al crear la cuenta'
  } finally {
    submitting.value = false
  }
}

function openEdit(account) {
  editingId.value = account.id
  editForm.name = account.name
  editForm.type = account.type
  editError.value = ''
  showEditModal.value = true
}

async function editAccount() {
  editing.value = true
  editError.value = ''
  try {
    const { data } = await api.put(`/accounts/${editingId.value}`, { name: editForm.name, type: editForm.type })
    const idx = accounts.value.findIndex((a) => a.id === editingId.value)
    if (idx !== -1) accounts.value[idx] = data
    showEditModal.value = false
  } catch (e) {
    editError.value = e.response?.data?.detail || 'Error al actualizar la cuenta'
  } finally {
    editing.value = false
  }
}

async function deleteAccount(id) {
  if (!confirm('Eliminar esta cuenta?')) return
  try {
    await api.delete(`/accounts/${id}`)
    accounts.value = accounts.value.filter((a) => a.id !== id)
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadAccounts)
</script>

<style scoped>
.accounts-page {
  max-width: 960px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: var(--spacing-xl);
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-neutral-900);
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}
.account-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}
.account-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.account-body {
  flex: 1;
  min-width: 0;
}
.account-name {
  display: block;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-neutral-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.account-type {
  display: block;
  font-size: 0.75rem;
  color: var(--color-neutral-400);
  margin-top: 2px;
}
.account-balance {
  text-align: right;
  flex-shrink: 0;
}
.account-currency {
  display: block;
  font-size: 0.7rem;
  color: var(--color-neutral-400);
}
.account-amount {
  display: block;
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-neutral-900);
}
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-neutral-400);
  font-size: 0.875rem;
}
.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: var(--spacing-md);
}
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.form-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  outline: none;
  transition: border-color var(--transition-fast);
}
.form-select:focus {
  border-color: var(--color-primary-400);
}
.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { font-size: 0.8rem; padding: var(--spacing-xs) var(--spacing-md); }
.btn-primary {
  background: var(--color-primary-600);
  color: white;
}
.account-actions {
  display: flex;
  gap: var(--spacing-xs);
  margin-left: var(--spacing-sm);
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  width: 420px;
  max-width: 90vw;
  box-shadow: var(--shadow-xl);
}
.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin-bottom: var(--spacing-lg);
}
.btn-danger {
  background: var(--color-error-600);
  color: white;
}
.btn-danger:hover:not(:disabled) { background: var(--color-error-700); }
.btn-outline {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  color: var(--color-neutral-700);
}
.btn-outline:hover { border-color: var(--color-primary-400); color: var(--color-primary-600); }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-700); }

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .accounts-page {
    padding: 0;
  }
  .account-card {
    flex-wrap: wrap;
  }
  .account-actions {
    width: 100%;
    margin-left: 0;
    margin-top: var(--spacing-sm);
    justify-content: flex-end;
  }
  .modal {
    width: 95%;
    max-height: 90vh;
    margin: var(--spacing-md);
  }
}
</style>

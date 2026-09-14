<template>
  <div class="accounts-tab">
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
            <span class="account-amount">${{ fmtAcc(account.balance, 2) }}</span>
          </div>
          <div class="account-actions">
            <button class="btn-icon-edit" @click="openEditAccount(account)" aria-label="Editar cuenta">
              <Pencil :size="14" />
            </button>
            <button class="btn-icon-danger" @click="confirmDeleteAccount(account.id)" aria-label="Eliminar cuenta">
              <X :size="14" />
            </button>
          </div>
        </div>

        <div v-if="!accounts.length" class="empty-state">
          <Wallet :size="48" class="empty-icon" />
          <p class="empty-text">No tienes cuentas creadas</p>
          <span class="empty-hint">Crea tu primera cuenta para comenzar</span>
        </div>
      </div>

      <div class="card form-card">
        <h3 class="section-title">{{ editingAccountId ? 'Editar cuenta' : 'Nueva cuenta' }}</h3>
        <form class="form" @submit.prevent="onAccountSubmit" novalidate>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="account-name">Nombre</label>
              <input id="account-name" name="name" v-model="accForm.name" class="form-input" type="text" required placeholder="Nombre de la cuenta" autocomplete="off" />
            </div>
            <div class="form-group">
              <label class="form-label" for="account-type">Tipo</label>
              <select id="account-type" name="type" v-model="accForm.type" class="form-select" required autocomplete="off">
                <option value="cash">Efectivo</option>
                <option value="bank">Banco</option>
                <option value="wallet">Billetera</option>
                <option value="credit_card">Tarjeta de crédito</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="account-balance">Saldo inicial</label>
              <div class="modal-amount-input">
                <span class="modal-currency">$</span>
                <input
                  id="account-balance"
                  name="balance"
                  :value="balanceDisplay"
                  @input="onBalanceInput"
                  @focus="balanceFmt.onFocus($event)"
                  class="modal-amount-field"
                  type="text"
                  inputmode="decimal"
                  required
                />
              </div>
            </div>
          </div>
          <div class="form-actions">
            <span v-if="accFormError" class="form-error" role="alert" aria-live="assertive">{{ accFormError }}</span>
            <button v-if="editingAccountId" class="btn btn-secondary" type="button" @click="cancelEditAccount">
              Cancelar
            </button>
            <button class="btn btn-primary" type="submit" :disabled="accSubmitting">
              {{ editingAccountId ? 'Guardar cambios' : (accSubmitting ? 'Creando...' : 'Crear cuenta') }}
            </button>
          </div>
        </form>
      </div>
    </template>

    <ConfirmDialog
      v-model="showAccConfirm"
      title="Eliminar cuenta"
      :message="accRecurringCount > 0 ? `¿Seguro que quieres eliminar esta cuenta? Tiene ${accRecurringCount} pago(s) recurrente(s) asociado(s). Al eliminarla, esos pagos quedarán sin cuenta asociada.` : '¿Seguro que quieres eliminar esta cuenta? Se perderán todos los datos asociados.'"
      confirm-text="Eliminar"
      cancel-text="Cancelar"
      type="danger"
      @confirm="handleDeleteAccountConfirm"
      @cancel="showAccConfirm = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { Pencil, X, Wallet, Banknote, CreditCard, PiggyBank } from 'lucide-vue-next'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useCurrency } from '@/composables/useCurrency'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const { fmt: fmtAcc } = useCurrency()
const toast = useToast()

const accounts = ref([])
const accLoading = ref(true)
const accSubmitting = ref(false)
const accFormError = ref('')
const accForm = reactive({ name: '', type: 'cash', balance: 0, currency: 'COP' })
const balanceFmt = useFormattedNumber(0, { prefix: '' })
const balanceDisplay = computed(() => balanceFmt.displayValue.value)

watch(
  () => balanceFmt.rawValue.value,
  (val) => {
    accForm.balance = Number(val) || 0
  }
)

function onBalanceInput(event) {
  balanceFmt.onInput(event)
}

const accToDelete = ref(null)
const showAccConfirm = ref(false)
const editingAccountId = ref(null)
const accRecurringCount = ref(0)

function confirmDeleteAccount(id) {
  accToDelete.value = id
  accRecurringCount.value = 0
  showAccConfirm.value = true
  api.get('/recurring-payments').then(({ data }) => {
    accRecurringCount.value = data.filter(r => r.account_id === id).length
  }).catch(() => {
    accRecurringCount.value = 0
  })
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
    accRecurringCount.value = 0
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
    balanceFmt.setInitial(0)
    toast.success('Cuenta creada')
  } catch (e) {
    accFormError.value = e.response?.data?.detail || 'No pudimos crear la cuenta'
  } finally {
    accSubmitting.value = false
  }
}

async function onAccountSubmit() {
  if (editingAccountId.value) {
    await updateAccount()
  } else {
    await createAccount()
  }
}

function openEditAccount(account) {
  editingAccountId.value = account.id
  accForm.name = account.name
  accForm.type = account.type
  accForm.balance = Number(account.balance) || 0
  balanceFmt.setInitial(Number(account.balance) || 0)
  accFormError.value = ''
}

async function updateAccount() {
  if (!editingAccountId.value) return
  accSubmitting.value = true
  accFormError.value = ''
  try {
    const payload = {
      name: accForm.name,
      type: accForm.type,
      balance: accForm.balance,
    }
    const { data } = await api.put(`/accounts/${editingAccountId.value}`, payload)
    const idx = accounts.value.findIndex(a => a.id === editingAccountId.value)
    if (idx !== -1) accounts.value[idx] = data
    cancelEditAccount()
    toast.success('Cuenta actualizada')
  } catch (e) {
    accFormError.value = e.response?.data?.detail || 'No pudimos actualizar la cuenta'
  } finally {
    accSubmitting.value = false
  }
}

function cancelEditAccount() {
  editingAccountId.value = null
  accForm.name = ''
  accForm.type = 'cash'
  accForm.balance = 0
  balanceFmt.setInitial(0)
  accFormError.value = ''
}

onMounted(loadAccounts)
</script>

<style scoped>
.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.account-card {
  position: relative;
  overflow: hidden;
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  border: 1px solid var(--color-neutral-100);
}
.account-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.account-body { flex: 1; min-width: 0; }
.account-name { display: block; font-weight: 600; font-size: 0.85rem; color: var(--color-neutral-900); }
.account-type { display: block; font-size: 0.75rem; color: var(--color-neutral-400); margin-top: 2px; }
.account-balance { text-align: right; flex-shrink: 0; }
.account-currency { display: block; font-size: 0.7rem; color: var(--color-neutral-400); }
.account-amount { display: block; font-weight: 700; font-size: 0.9rem; color: var(--color-neutral-900); font-family: var(--font-mono); }
.account-actions { flex-shrink: 0; }

.btn-icon-edit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: none;
  border: none;
  color: var(--color-neutral-400);
  cursor: pointer;
  padding: 0;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.btn-icon-edit:hover { color: var(--color-primary-600); background: var(--color-primary-50); }
.btn-icon-edit:active:not(:disabled) { transform: scale(0.94); }

.btn-icon-danger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: none;
  border: none;
  color: var(--color-neutral-400);
  cursor: pointer;
  padding: 0;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.btn-icon-danger:hover { color: var(--color-error-500); background: var(--color-error-50); }
.btn-icon-danger:active:not(:disabled) { transform: scale(0.94); }

.form-card { margin-bottom: var(--spacing-md); }
.form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.form-label { font-size: 0.8rem; font-weight: 500; color: var(--color-neutral-700); }
.form-input, .form-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  outline: none;
  transition: border-color var(--transition-fast);
}
.form-actions { display: flex; align-items: center; justify-content: flex-end; gap: var(--spacing-md); margin-top: var(--spacing-sm); }
.form-error { color: var(--color-error-500); font-size: 0.8rem; margin-right: auto; }

.modal-amount-input {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  transition: border-color var(--transition-fast);
  min-height: 44px;
  min-width: 0;
}
.modal-currency {
  font-size: 18px;
  color: var(--color-neutral-400);
  flex-shrink: 0;
}
.modal-amount-field {
  flex: 1;
  border: none;
  font-size: 18px;
  font-weight: 700;
  outline: none;
  background: transparent;
  font-family: var(--font-mono);
  min-height: 44px;
  min-width: 0;
}

@media (max-width: 640px) {
  .form-row { grid-template-columns: 1fr; }
  .accounts-grid { grid-template-columns: 1fr; }
}
</style>

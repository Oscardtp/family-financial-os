<template>
  <div class="recurring-page">
    <div class="recurring-header">
      <h1 class="page-title">Pagos recurrentes</h1>
      <p class="page-subtitle">Administra tus gastos e ingresos que se repiten</p>
    </div>

    <div v-if="loading" class="recurring-loading">
      <div class="spinner-large" />
    </div>

    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <button class="btn btn-click" @click="store.fetchAll">Reintentar</button>
    </div>

    <template v-else>
      <div v-if="activeItems.length === 0" class="recurring-empty">
        <Receipt :size="48" class="empty-icon" />
        <h3>No tienes pagos recurrentes</h3>
        <p class="empty-text">Agégalos desde el botón + en el Resumen o aquí mismo.</p>
        <button class="btn btn-click" @click="openCreate">
          <Plus :size="18" /> Crear pago recurrente
        </button>
      </div>

      <div v-else class="recurring-list">
        <div class="recurring-section">
          <h2 class="section-title">Activos</h2>
          <RecurringCard
            v-for="p in activeItems"
            :key="p.id"
            :payment="p"
            @pay="handlePay"
            @history="openHistory"
            @edit="openEdit"
            @toggle-active="handleToggleActive"
          />
        </div>

        <div v-if="inactiveItems.length > 0" class="recurring-section">
          <h2 class="section-title">Inactivos</h2>
          <RecurringCard
            v-for="p in inactiveItems"
            :key="p.id"
            :payment="p"
            @pay="handlePay"
            @history="openHistory"
            @edit="openEdit"
            @toggle-active="handleToggleActive"
          />
        </div>
      </div>
    </template>

    <button class="fab" @click="openCreate" aria-label="Crear pago recurrente">
      <Plus :size="24" />
    </button>

    <RecurringHistorySheet
      :open="historyOpen"
      :recurring-id="selectedPayment?.id"
      :recurring-name="selectedPayment?.name"
      @close="historyOpen = false"
    />

    <RecurringEditModal
      v-if="editOpen"
      :payment="selectedPayment"
      @close="editOpen = false"
      @save="handleEditSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Receipt, Plus } from 'lucide-vue-next'
import { useRecurringPaymentsStore } from '@/stores/recurringPayments'
import RecurringCard from '@/components/recurring/RecurringCard.vue'
import RecurringHistorySheet from '@/components/recurring/RecurringHistorySheet.vue'
import RecurringEditModal from '@/components/recurring/RecurringEditModal.vue'

const store = useRecurringPaymentsStore()
const historyOpen = ref(false)
const editOpen = ref(false)
const selectedPayment = ref(null)

const activeItems = computed(() => store.items.filter(p => p.is_active))
const inactiveItems = computed(() => store.items.filter(p => !p.is_active))

const loading = computed(() => store.loading)
const error = computed(() => store.error)

onMounted(() => {
  store.fetchAll()
})

async function handlePay(p) {
  await store.pay(p.id)
}

function openHistory(p) {
  selectedPayment.value = p
  historyOpen.value = true
}

function openEdit(p) {
  selectedPayment.value = p
  editOpen.value = true
}

function openCreate() {
  selectedPayment.value = null
  editOpen.value = true
}

async function handleToggleActive(p) {
  await store.toggleActive(p.id)
}

async function handleEditSave(data) {
  if (data.id) {
    await store.update(data.id, data)
  } else {
    const { id, ...createData } = data
    await store.create(createData)
  }
  editOpen.value = false
  selectedPayment.value = null
}
</script>

<style scoped>
.recurring-page {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-md);
}
.recurring-header {
  margin-bottom: var(--spacing-lg);
}
.page-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin: 0;
}
.page-subtitle {
  color: var(--color-neutral-500);
  font-size: 0.9rem;
  margin: 4px 0 0;
}
.recurring-loading {
  display: flex;
  justify-content: center;
  padding: 64px 0;
}
.recurring-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.recurring-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
.section-title {
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-neutral-500);
  margin: 0 0 var(--spacing-xs);
}
.recurring-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: 64px 0;
  text-align: center;
}
.empty-icon {
  color: var(--color-neutral-300);
}
.empty-text {
  color: var(--color-neutral-500);
  font-size: 0.9rem;
}
.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: var(--color-primary-600);
  color: var(--color-neutral-0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  transition: transform var(--transition-fast), background var(--transition-fast);
}
.fab:hover {
  background: var(--color-primary-700);
}
.fab:active { transform: scale(0.96); }
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
  color: var(--color-error-500);
}
.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform var(--transition-fast);
}
.btn-click {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
}
.btn-click:active { transform: scale(0.96); }
.spinner-large {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>

<template>
  <div class="fab-container">
    <button class="fab-button" @click="openModal" title="Registro rápido" aria-label="Abrir registro rápido">
      <Plus :size="24" />
    </button>

    <Teleport to="body">
      <div v-if="isOpen" class="fab-overlay" @click="closeModal">
        <div class="fab-modal" @click.stop role="dialog" aria-modal="true">
          <div class="drag-handle"></div>
          <div class="fab-modal-header">
            <h3 id="fab-title" aria-live="polite">{{ headerTitle }}</h3>
            <button class="fab-close" @click="closeModal" aria-label="Cerrar">
              <X :size="20" />
            </button>
          </div>

          <TypeSelector v-if="step === 'type'" @select="handleTypeSelect" />

          <template v-else-if="step === 'form'">
            <button class="back-btn" @click="step = 'type'">← Cambiar</button>

            <TransactionForm
              v-if="selectedType === 'expense' || selectedType === 'income'"
              :type="selectedType"
              :categories="categories"
              :debts="debts"
              :loading="submitting"
              @submit="handleTransactionSubmit"
            />

            <RecurringForm
              v-else-if="selectedType === 'recurring'"
              :loading="submitting"
              @submit="handleRecurringSubmit"
            />

            <GoalForm
              v-else-if="selectedType === 'goal'"
              :loading="submitting"
              @submit="handleGoalSubmit"
            />
          </template>

          <SourcePicker
            v-else-if="step === 'source'"
            :amount="lastAmount"
            :accounts="accounts"
            @confirm="handleSourceConfirm"
          />

          <DoneConfirmation v-else-if="step === 'done'" :type="selectedType" @close="closeModal" />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Plus, X } from 'lucide-vue-next'
import api from '@/services/api'
import { useGoalsStore } from '@/stores/goals'
import TypeSelector from './TypeSelector.vue'
import TransactionForm from './TransactionForm.vue'
import RecurringForm from './RecurringForm.vue'
import GoalForm from './GoalForm.vue'
import SourcePicker from './SourcePicker.vue'
import DoneConfirmation from './DoneConfirmation.vue'

const goalsStore = useGoalsStore()

function haptic(ms = 10) {
  navigator.vibrate?.(ms)
}

function handleKeydown(e) {
  if (e.key === 'Escape' && isOpen.value) closeModal()
}

onMounted(() => document.addEventListener('keydown', handleKeydown))
onUnmounted(() => document.removeEventListener('keydown', handleKeydown))

const props = defineProps({
  accounts: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
  debts: { type: Array, default: () => [] },
})

const emit = defineEmits(['transaction-created'])

const isOpen = ref(false)
const step = ref('type')
const selectedType = ref(null)
const submitting = ref(false)
const lastAmount = ref(0)
const lastCategoryId = ref(0)

const headerTitle = computed(() => {
  const titles = {
    type: '¿Qué vas a registrar?',
    source: '¿De cuál cuenta?',
    done: '¡Listo!',
    expense: '¿Cuánto pagaste?',
    income: '¿Cuánto recibiste?',
    recurring: 'Configura tu pago fijo',
    goal: '¿Para qué estás ahorrando?',
  }
  return titles[step.value === 'form' ? selectedType.value : step.value] || 'Agregar'
})

function openModal() {
  isOpen.value = true
  step.value = 'type'
  selectedType.value = null
  haptic()
}

function closeModal() {
  isOpen.value = false
  step.value = 'type'
  selectedType.value = null
}

function handleTypeSelect(type) {
  selectedType.value = type
  step.value = 'form'
  haptic()
}

async function handleTransactionSubmit(data) {
  submitting.value = true
  try {
    const today = new Date().toISOString().split('T')[0]
    await api.post('/transactions', {
      account_id: props.accounts[0]?.id,
      amount: data.amount,
      category_id: data.category_id,
      type: selectedType.value,
      description: data.description,
      date: today,
    })
    lastAmount.value = data.amount
    lastCategoryId.value = data.category_id
    step.value = 'source'
    emit('transaction-created')
  } catch (e) {
    window.$toast?.error(e.response?.data?.detail || 'No pude guardar. ¿Los datos están bien?')
  } finally {
    submitting.value = false
  }
}

async function handleRecurringSubmit(data) {
  submitting.value = true
  try {
    await api.post('/recurring-payments', {
      name: data.name,
      amount: data.amount,
      type: 'expense',
      frequency: data.frequency,
      day_of_month: data.day_of_month,
      account_id: props.accounts[0]?.id,
      is_active: true,
    })
    step.value = 'done'
    emit('transaction-created')
  } catch (e) {
    window.$toast?.error(e.response?.data?.detail || 'No pude activar el pago. ¿Los datos están bien?')
  } finally {
    submitting.value = false
  }
}

async function handleGoalSubmit(data) {
  submitting.value = true
  const { error: err } = await goalsStore.createGoal(data)
  submitting.value = false
  if (err) {
    window.$toast?.error(err)
  } else {
    step.value = 'done'
    emit('transaction-created')
  }
}

async function handleSourceConfirm({ account_id, remember }) {
  if (remember && lastCategoryId.value) {
    api.post('/preferences', {
      category_id: lastCategoryId.value,
      account_id,
    }).catch(() => {})
  }
  step.value = 'done'
}
</script>

<style scoped>
.fab-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.fab-button {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: var(--shadow-xl);
  transition: all var(--transition-fast);
}

.fab-button:hover { filter: brightness(1.1); transform: scale(1.05); }
.fab-button:active { transform: scale(0.95); }

@keyframes fab-pulse {
  0%, 100% { box-shadow: var(--shadow-xl); }
  50% { box-shadow: var(--shadow-xl), 0 0 0 8px rgba(47, 113, 229, 0.12); }
}
.fab-button { animation: fab-pulse 4s ease-in-out infinite; }
.fab-button:hover { animation: none; }

.fab-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1001;
  padding: var(--spacing-md);
  animation: fadeIn 150ms ease;
}

.fab-modal {
  width: 100%;
  max-width: 400px;
  background: var(--color-neutral-0);
  border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
  padding: var(--spacing-lg);
  padding-top: var(--spacing-sm);
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 200ms ease;
}

.drag-handle {
  width: 32px;
  height: 4px;
  background: var(--color-neutral-300);
  border-radius: var(--radius-full);
  margin: 0 auto var(--spacing-md);
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.fab-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.fab-modal-header h3 { margin: 0; font-size: 18px; color: var(--color-neutral-900); }

.fab-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-neutral-500);
  padding: var(--spacing-xs);
  border-radius: var(--radius-md);
}

.fab-close:hover { background: var(--color-neutral-100); }

.back-btn {
  background: none;
  border: none;
  color: var(--color-primary-600);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  margin-bottom: var(--spacing-md);
}

.back-btn:hover { color: var(--color-primary-700); }

@media (max-width: 640px) {
  .fab-container { bottom: 80px; right: 16px; }
}
</style>

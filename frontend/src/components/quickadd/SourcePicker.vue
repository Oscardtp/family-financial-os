<template>
  <div class="source-picker">
    <div class="success-icon">
      <CheckCircle :size="48" />
    </div>
    <p class="amount-display">${{ fmt(amount) }}</p>
    <p class="question">¿De dónde salió?</p>

    <div class="source-grid">
      <button
        v-for="source in sources"
        :key="source.id"
        class="source-btn"
        :class="{ selected: selectedId === source.id }"
        @click="selectedId = source.id"
      >
        <span class="source-icon">{{ source.icon }}</span>
        <span class="source-name">{{ source.name }}</span>
      </button>
    </div>

    <label class="remember-check">
      <input type="checkbox" v-model="remember">
      Recordar para esta categoría
    </label>

    <button
      class="confirm-btn"
      @click="handleConfirm"
      :disabled="!selectedId"
    >
      Confirmar
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { CheckCircle } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  amount: { type: Number, required: true },
  accounts: { type: Array, default: () => [] },
})

const emit = defineEmits(['confirm'])

const selectedId = ref(0)
const remember = ref(false)

const sources = computed(() =>
  props.accounts.map(a => ({
    id: a.id,
    name: a.name,
    icon: a.type === 'bank' ? '🏦' : a.type === 'cash' ? '💵' : '📱',
  }))
)

function handleConfirm() {
  if (!selectedId.value) return
  emit('confirm', { account_id: selectedId.value, remember: remember.value })
}
</script>

<style scoped>
.source-picker { text-align: center; padding: var(--spacing-md) 0; }

.success-icon { color: var(--color-success-500); margin-bottom: var(--spacing-md); }

.amount-display {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-neutral-900);
  margin: 0 0 var(--spacing-xs);
}

.question {
  font-size: 16px;
  color: var(--color-neutral-600);
  margin: 0 0 var(--spacing-lg);
}

.source-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.source-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  background: var(--color-neutral-0);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.source-btn:hover { border-color: var(--color-primary-300); }
.source-btn.selected { border-color: var(--color-primary-500); background: var(--color-primary-50); }

.source-icon { font-size: 24px; }
.source-name { font-size: 12px; font-weight: 500; color: var(--color-neutral-700); }

.remember-check {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-size: 13px;
  color: var(--color-neutral-600);
  margin-bottom: var(--spacing-lg);
  cursor: pointer;
}

.confirm-btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: var(--color-primary-500);
  cursor: pointer;
}

.confirm-btn:hover:not(:disabled) { opacity: 0.9; }
.confirm-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

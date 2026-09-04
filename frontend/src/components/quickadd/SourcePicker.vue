<template>
  <div class="source-picker">
    <div class="success-icon">
      <CheckCircle :size="48" />
    </div>
    <p class="amount-display">${{ fmt(amount) }}</p>
    <p class="question">¿De cuál cuenta lo sacas?</p>

    <div class="source-grid">
      <button
        v-for="source in sources"
        :key="source.id"
        class="source-btn"
        :class="{ selected: selectedId === source.id }"
        @click="selectedId = source.id"
        :aria-label="'Cuenta: ' + source.name"
      >
        <span class="source-icon"><component :is="source.icon" :size="24" /></span>
        <span class="source-name">{{ source.name }}</span>
      </button>
    </div>

    <label class="remember-check">
      <input type="checkbox" v-model="remember">
      ¿Siempre de esta cuenta?
    </label>

    <button
      ref="confirmBtn"
      class="confirm-btn"
      @click="handleConfirm"
      :disabled="!selectedId"
      aria-label="Listo"
    >
      Listo
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { CheckCircle, Building2, Banknote, Smartphone } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'

const { fmt } = useCurrency()

const props = defineProps({
  amount: { type: Number, required: true },
  accounts: { type: Array, default: () => [] },
  preferredAccountId: { type: Number, default: 0 },
})

const emit = defineEmits(['confirm'])

const selectedId = ref(0)
const remember = ref(false)
const confirmBtn = ref(null)

const sources = computed(() =>
  props.accounts.map(a => ({
    id: a.id,
    name: a.name,
    icon: a.type === 'bank' ? Building2 : a.type === 'cash' ? Banknote : Smartphone,
  }))
)

onMounted(async () => {
  if (props.preferredAccountId) {
    selectedId.value = props.preferredAccountId
  } else if (props.accounts.length === 1) {
    selectedId.value = props.accounts[0].id
  }
  await nextTick()
  confirmBtn.value?.focus()
})

function handleConfirm() {
  if (!selectedId.value) return
  emit('confirm', { account_id: selectedId.value, remember: remember.value })
}
</script>

<style scoped>
.source-picker { text-align: center; padding: var(--spacing-md) 0; }

.success-icon { color: var(--color-success-500); margin-bottom: var(--spacing-md); }

.amount-display {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-neutral-900);
  margin: 0 0 var(--spacing-xs);
}

.question {
  font-size: var(--font-size-base);
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

.source-icon { font-size: var(--font-size-xl); }
.source-name { font-size: var(--font-size-xs); font-weight: 500; color: var(--color-neutral-700); }

.remember-check {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-600);
  margin-bottom: var(--spacing-lg);
  cursor: pointer;
}

.confirm-btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: white;
  background: var(--color-primary-500);
  cursor: pointer;
}

.confirm-btn:hover:not(:disabled) { opacity: 0.9; }
.confirm-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

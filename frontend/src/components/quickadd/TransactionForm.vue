<template>
  <form class="transaction-form" @submit.prevent="handleSubmit">
    <div class="form-field">
      <label class="form-question">
        {{ type === 'expense' ? '¿Cuánto pagaste?' : '¿Cuánto recibiste?' }}
      </label>
      <div class="amount-input" :class="{ error: submitted && !amount }">
        <span class="currency">$</span>
        <input
          ref="amountRef"
          :value="displayAmount"
          @input="onAmountInput"
          @focus="onAmountFocus"
          class="amount-field"
          :placeholder="type === 'expense' ? 'Ej: 45.000' : 'Ej: 800.000'"
          aria-label="Monto"
        >
      </div>
      <span v-if="submitted && !amount" class="field-error">¿Cuánto fue?</span>
    </div>

    <div class="form-field">
      <label class="form-question">¿En qué?</label>
      <input
        v-if="filteredCategories.length > 4"
        v-model="catSearch"
        type="text"
        class="cat-search"
        placeholder="Buscar categoría..."
      >
      <div v-if="displayCategories.length" class="category-grid">
        <button
          v-for="cat in displayCategories"
          :key="cat.id"
          type="button"
          class="category-btn"
          :class="{ selected: categoryId === cat.id }"
          @click="categoryId = cat.id"
          :aria-label="'Categoría: ' + cat.name"
        >
          <span class="cat-emoji">{{ cat.icon || '📦' }}</span>
          <span class="cat-name">{{ cat.name }}</span>
        </button>
      </div>
      <p v-else class="empty-msg">{{ catSearch ? 'No encontré esa categoría' : 'Primero crea categorías en ajustes' }}</p>
      <span v-if="submitted && !categoryId" class="field-error">¿En qué te gastaste?</span>
    </div>

    <div v-if="isDebtCategory" class="form-field">
      <label class="form-question">¿Qué deuda?</label>
      <select v-model="debtId" class="form-select" aria-label="Seleccionar deuda">
        <option :value="0" disabled>Seleccionar deuda</option>
        <option v-for="d in debts" :key="d.id" :value="d.id">
          {{ d.name }} (${{ fmtCurrency(d.current_balance ?? 0) }})
        </option>
      </select>
      <span v-if="submitted && !debtId" class="field-error">Selecciona la deuda</span>
    </div>

    <div class="form-field">
      <input
        v-model="description"
        type="text"
        class="text-input"
        placeholder="Nota rápida (si quieres)"
      >
    </div>

    <button type="submit" class="submit-btn" :class="type" :disabled="loading" :aria-label="type === 'expense' ? 'Guardar gasto' : 'Guardar ingreso'">
      <span v-if="loading" class="spinner"></span>
      {{ loading ? 'Guardando...' : type === 'expense' ? 'Guardar gasto' : 'Guardar ingreso' }}
    </button>
  </form>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useFormattedNumber } from '@/composables/useFormattedNumber'
import { useCurrency } from '@/composables/useCurrency'

const { fmt: fmtCurrency } = useCurrency()

const props = defineProps({
  type: { type: String, required: true },
  categories: { type: Array, default: () => [] },
  debts: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'back'])

const amountRef = ref(null)
const submitted = ref(false)
const description = ref('')
const categoryId = ref(0)
const debtId = ref(0)
const catSearch = ref('')

let fmt = useFormattedNumber(0, { prefix: '' })
const amount = computed(() => fmt.rawValue.value)
const displayAmount = computed(() => fmt.displayValue.value)

const onAmountInput = (event) => fmt.onInput(event)
const onAmountFocus = (event) => fmt.onFocus(event)

const filteredCategories = computed(() =>
  props.categories.filter(c => c.type === props.type)
)

const displayCategories = computed(() => {
  if (!catSearch.value) return filteredCategories.value
  const q = catSearch.value.toLowerCase()
  return filteredCategories.value.filter(c => c.name?.toLowerCase().includes(q))
})

const isDebtCategory = computed(() => {
  if (props.type !== 'expense') return false
  const debtCat = filteredCategories.value.find(c => c.name?.toLowerCase() === 'deudas')
  return debtCat && categoryId.value === debtCat.id
})

onMounted(() => nextTick(() => amountRef.value?.focus()))

function handleSubmit() {
  submitted.value = true
  if (!amount.value || !categoryId.value) return
  if (isDebtCategory.value && !debtId.value) return

  emit('submit', {
    amount: amount.value,
    category_id: categoryId.value,
    debt_id: isDebtCategory.value ? debtId.value : null,
    description: description.value || null,
  })
}
</script>

<style scoped>
.form-field { margin-bottom: var(--spacing-lg); }

.form-question {
  display: block;
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-neutral-700);
  margin-bottom: var(--spacing-sm);
}

.amount-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  transition: border-color var(--transition-fast);
}

.amount-input:focus-within { border-color: var(--color-primary-500); }
.amount-input.error { border-color: var(--color-error-400); }

.currency { font-size: var(--font-size-xl); color: var(--color-neutral-400); }

.amount-field {
  flex: 1;
  border: none;
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-neutral-900);
  outline: none;
  width: 100%;
  background: transparent;
}

.amount-field::placeholder { color: var(--color-neutral-300); }

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-sm);
}

.category-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  background: var(--color-neutral-0);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.category-btn:hover { border-color: var(--color-primary-300); }
.category-btn.selected { border-color: var(--color-primary-500); background: var(--color-primary-50); }
.category-btn.selected::after {
  content: '✓';
  position: absolute;
  top: 2px;
  right: 2px;
  background: var(--color-primary-500);
  color: white;
  border-radius: var(--radius-full);
  width: 16px;
  height: 16px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.cat-emoji { font-size: 20px; }
.cat-name { font-size: var(--font-size-xs); color: var(--color-neutral-600); text-align: center; }

.empty-msg {
  text-align: center;
  color: var(--color-neutral-400);
  font-size: var(--font-size-sm);
  padding: var(--spacing-md);
}

.cat-search {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
  margin-bottom: var(--spacing-sm);
  outline: none;
}

.cat-search:focus { border-color: var(--color-primary-500); }

.form-select {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
  background: var(--color-neutral-0);
  transition: border-color var(--transition-fast);
}

.form-select:focus { border-color: var(--color-primary-500); outline: none; }

.text-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-neutral-700);
  transition: border-color var(--transition-fast);
}

.text-input:focus { border-color: var(--color-primary-500); outline: none; }

.field-error {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-error-500);
  margin-top: var(--spacing-xs);
}

.submit-btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.submit-btn.expense { background: var(--color-error-500); }
.submit-btn.income { background: var(--color-success-500); }
.submit-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .category-grid { grid-template-columns: repeat(3, 1fr); }
  .amount-field { font-size: var(--font-size-xl); }
  .currency { font-size: var(--font-size-lg); }
}
</style>

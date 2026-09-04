<template>
  <div class="type-selector">
    <button ref="firstBtn" class="type-btn expense" @click="$emit('select', 'expense')" aria-label="Registrar gasto">
      <span class="type-icon"><Wallet :size="24" /></span>
      <span class="type-label">Gasto</span>
      <span class="type-hint">Plata que sale</span>
    </button>
    <button class="type-btn income" @click="$emit('select', 'income')" aria-label="Registrar ingreso">
      <span class="type-icon"><TrendingUp :size="24" /></span>
      <span class="type-label">Ingreso</span>
      <span class="type-hint">Plata que entra</span>
    </button>
    <button class="type-btn recurring" @click="$emit('select', 'recurring')" aria-label="Configurar pago recurrente">
      <span class="type-icon"><RefreshCw :size="24" /></span>
      <span class="type-label">Recurrente</span>
      <span class="type-hint">Se paga siempre igual</span>
    </button>
    <button class="type-btn goal" @click="$emit('select', 'goal')" aria-label="Crear meta de ahorro">
      <span class="type-icon"><Target :size="24" /></span>
      <span class="type-label">Meta</span>
      <span class="type-hint">Es para ahorrar</span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Wallet, TrendingUp, RefreshCw, Target } from 'lucide-vue-next'
defineEmits(['select'])

const firstBtn = ref(null)
onMounted(() => firstBtn.value?.focus())
</script>

<style scoped>
.type-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.type-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-lg) var(--spacing-sm);
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  background: var(--color-neutral-0);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.type-btn:hover {
  border-color: var(--color-primary-300);
  background: var(--color-primary-50);
}

.type-btn.expense:hover { border-color: var(--color-error-300); background: var(--color-error-50); }
.type-btn.income:hover { border-color: var(--color-success-300); background: var(--color-success-50); }
.type-btn.recurring:hover { border-color: var(--color-warning-300); background: var(--color-warning-50); }
.type-btn.goal:hover { border-color: var(--color-info-300); background: var(--color-info-50); }

.type-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.type-btn.expense .type-icon { color: var(--color-error-500); background: var(--color-error-50); }
.type-btn.income .type-icon { color: var(--color-success-500); background: var(--color-success-50); }
.type-btn.recurring .type-icon { color: var(--color-warning-500); background: var(--color-warning-50); }
.type-btn.goal .type-icon { color: var(--color-info-500); background: var(--color-info-50); }

.type-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-neutral-800);
}

.type-hint {
  font-size: 11px;
  color: var(--color-neutral-400);
  text-align: center;
  line-height: 1.2;
}

@media (max-width: 640px) {
  .type-btn { padding: var(--spacing-md) var(--spacing-xs); }
  .type-icon { width: 36px; height: 36px; }
  .type-hint { display: none; }
}
</style>

<template>
  <div class="goal-scenario-simulator card">
    <h4 class="simulator-title">¿Qué pasa si ahorro más al mes?</h4>
    <div class="simulator-controls">
      <label class="simulator-label" for="extra-contribution">Aporte extra mensual</label>
      <div class="simulator-input-row">
        <span class="simulator-currency">$</span>
        <input
          id="extra-contribution"
          v-model="extraAmount"
          type="number"
          class="simulator-input"
          placeholder="0"
          min="0"
          step="10000"
        />
      </div>
      <div class="simulator-presets">
        <button
          v-for="preset in presets"
          :key="preset"
          type="button"
          class="preset-btn"
          :class="{ active: Number(extraAmount) === preset }"
          @click="extraAmount = String(preset)"
        >
          {{ fmt(preset) }}
        </button>
      </div>
      <button
        class="simulate-btn"
        :disabled="loading || !canSimulate"
        @click="runSimulation"
      >
        {{ loading ? 'Calculando...' : 'Simular' }}
      </button>
    </div>
    <div v-if="scenarioError" class="simulator-error">{{ scenarioError }}</div>
    <div v-if="scenarioResult" class="simulator-result">
      <div class="result-row">
        <span class="result-label">Valor proyectado</span>
        <span class="result-value">{{ fmt(scenarioResult.projected_value) }}</span>
      </div>
      <div v-if="scenarioResult.months_to_goal" class="result-row">
        <span class="result-label">Meses para meta</span>
        <span class="result-value">{{ scenarioResult.months_to_goal }}</span>
      </div>
      <div class="result-row">
        <span class="result-label">Varianza</span>
        <GoalVariance :projected-value="scenarioResult.projected_value" :target-amount="goal.target_amount" />
      </div>
      <span class="simulator-badge">PROYECCIÓN</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGoalProjection } from '@/composables/useGoalProjection'
import { useCurrency } from '@/composables/useCurrency'
import GoalVariance from './GoalVariance.vue'

const props = defineProps({
  goal: { type: Object, default: null },
})

const { calculateProjection, loading } = useGoalProjection()
const { fmt } = useCurrency()

const extraAmount = ref('0')
const scenarioResult = ref(null)
const scenarioError = ref(null)
const simTimer = ref(null)

const presets = [0, 25000, 50000, 100000]

const canSimulate = computed(() => {
  const num = Number(extraAmount.value)
  return Number.isFinite(num) && num >= 0 && props.goal?.target_amount > 0
})

watch(extraAmount, (val) => {
  scenarioResult.value = null
  scenarioError.value = null
})

async function runSimulation() {
  if (!props.goal) return
  const extra = Number(extraAmount.value) || 0
  const payload = {
    current_amount: Number(props.goal.current_amount) || 0,
    monthly_contribution: (Number(props.goal.monthly_contribution) || 0) + extra,
    target_amount: Number(props.goal.target_amount) || 0,
    expected_return_rate: props.goal.expected_return_rate ?? null,
    horizon_months: props.goal.horizon_months ?? null,
  }
  try {
    scenarioError.value = null
    const data = await calculateProjection(payload)
    scenarioResult.value = data
  } catch {
    scenarioError.value = 'No pudimos calcular la simulación. Intenta de nuevo.'
  }
}

defineExpose({ runSimulation })
</script>
<style scoped>
.goal-scenario-simulator {
  padding: 16px;
  margin-top: 12px;
}

.simulator-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-neutral-800);
  margin: 0 0 12px;
}

.simulator-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.simulator-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-neutral-600);
}

.simulator-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 2px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  min-height: 44px;
  transition: border-color var(--transition-fast);
}

.simulator-input-row:focus-within {
  border-color: var(--color-primary-500);
}

.simulator-currency {
  font-size: 16px;
  color: var(--color-neutral-400);
  font-weight: 600;
}

.simulator-input {
  flex: 1;
  border: none;
  font-size: 16px;
  font-weight: 700;
  outline: none;
  background: transparent;
  font-family: var(--font-mono);
  min-height: 24px;
}

.simulator-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-btn {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
  border: none;
  border-radius: var(--radius-full);
  padding: 6px 14px;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-height: 36px;
}

.preset-btn:hover {
  background: var(--color-neutral-200);
}

.preset-btn.active {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

.simulate-btn {
  background: var(--color-info-500);
  color: white;
  border: none;
  border-radius: var(--radius-full);
  padding: 10px 20px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-height: 44px;
}

.simulate-btn:hover:not(:disabled) {
  background: var(--color-info-600);
}

.simulate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.simulator-error {
  margin-top: 10px;
  font-size: 0.8125rem;
  color: var(--color-error-600);
}

.simulator-result {
  margin-top: 14px;
  padding: 14px;
  background: var(--color-info-50);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-label {
  font-size: 0.8125rem;
  color: var(--color-neutral-600);
}

.result-value {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-neutral-900);
  font-family: var(--font-mono);
}

.simulator-badge {
  align-self: flex-start;
  background: var(--color-info-500);
  color: white;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  letter-spacing: 0.05em;
}
</style>

<template>
  <div class="bme" data-testid="method-editor">
    <p class="bme-hint">Ajusta los porcentajes. Deben sumar exactamente 100%.</p>

    <div class="bme-slider-list">
      <div v-for="(g, idx) in localGroups" :key="g.key" class="bme-slider-row">
        <label class="bme-slider-label" :for="`bme-${g.key}`">
          {{ g.label }}
        </label>
        <input
          :id="`bme-${g.key}`"
          type="range"
          class="bdm-form-input bdm-form-input--pct bme-range"
          min="0"
          max="100"
          step="1"
          :value="g.pct"
          @input="onInput(idx, $event.target.value)"
        />
        <span class="bme-pct" data-testid="group-pct">{{ g.pct }}%</span>
      </div>
    </div>

    <p class="bme-sum" :class="{ ok: sumValid, bad: !sumValid }" role="status" data-testid="sum-display">
      Suma: {{ sum }}% {{ sumValid ? '✓' : '— debe ser 100%' }}
    </p>

    <div class="bme-bar" aria-hidden="true" data-testid="visual-bar">
      <div
        v-for="g in localGroups"
        :key="g.key"
        class="bme-bar-segment"
        :style="{ width: Math.min(g.pct, 100) + '%' }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  groups: {
    type: Array,
    required: true,
    validator: (v) => Array.isArray(v) && v.every(g => 'key' in g && 'label' in g && 'pct' in g),
  },
})

const emit = defineEmits(['update'])

const localGroups = ref(props.groups.map(g => ({ ...g })))

watch(() => props.groups, (newGroups) => {
  localGroups.value = newGroups.map(g => ({ ...g }))
}, { deep: true })

const sum = computed(() => localGroups.value.reduce((acc, g) => acc + (Number(g.pct) || 0), 0))
const sumValid = computed(() => localGroups.value.length > 0 && sum.value === 100)

function onInput(idx, value) {
  localGroups.value[idx].pct = Number(value)
  emit('update', localGroups.value.map(g => ({ ...g })))
}
</script>

<style scoped>
.bme { display: flex; flex-direction: column; gap: var(--spacing-md); }
.bme-hint { font-size: var(--font-size-sm); color: var(--color-neutral-500); margin: 0; }
.bme-slider-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.bme-slider-row { display: flex; align-items: center; gap: var(--spacing-md); }
.bme-slider-label { font-size: 0.85rem; font-weight: 500; color: var(--color-neutral-700); min-width: 140px; }
.bme-range { flex: 1; height: 44px; -webkit-appearance: none; appearance: none; background: transparent; cursor: pointer; }
.bme-range::-webkit-slider-runnable-track { height: 6px; background: var(--color-neutral-200); border-radius: 3px; }
.bme-range::-webkit-slider-thumb { -webkit-appearance: none; width: 44px; height: 44px; border-radius: 50%; background: var(--color-primary-600); cursor: pointer; border: 2px solid var(--color-neutral-0); box-shadow: var(--shadow-sm); margin-top: -19px; }
.bme-range::-moz-range-track { height: 6px; background: var(--color-neutral-200); border-radius: 3px; }
.bme-range::-moz-range-thumb { width: 44px; height: 44px; border-radius: 50%; background: var(--color-primary-600); cursor: pointer; border: 2px solid var(--color-neutral-0); box-shadow: var(--shadow-sm); }
.bme-range:focus-visible { outline: 2px solid var(--color-primary-500); outline-offset: 2px; }
.bme-pct { font-family: var(--font-mono); font-size: 0.9rem; font-weight: 700; color: var(--color-neutral-900); min-width: 50px; text-align: right; }
.bme-sum { font-size: 0.85rem; font-weight: 600; margin: 0; }
.bme-sum.ok { color: var(--color-success-700); }
.bme-sum.bad { color: var(--color-error-600); }
.bme-bar { display: flex; height: 12px; border-radius: 6px; overflow: hidden; background: var(--color-neutral-100); }
.bme-bar-segment { height: 100%; background: var(--color-primary-600); transition: width var(--transition-fast); }
.bme-bar-segment:nth-child(2) { opacity: 0.75; }
.bme-bar-segment:nth-child(3) { opacity: 0.55; }
.bme-bar-segment:nth-child(4) { opacity: 0.42; }
.bme-bar-segment:nth-child(5) { opacity: 0.32; }
.bme-bar-segment:nth-child(6) { opacity: 0.24; }
@media (prefers-reduced-motion: reduce) { .bme-bar-segment { transition: none; } }
</style>
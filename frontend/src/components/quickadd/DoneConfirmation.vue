<template>
  <div class="done-confirmation">
    <div class="done-icon">
      <CheckCircle :size="64" />
    </div>
    <p class="done-text">{{ message }}</p>
    <p class="done-sub">{{ submessage }}</p>
    <button class="close-btn" @click="$emit('close')">Seguir</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CheckCircle } from 'lucide-vue-next'

const props = defineProps({
  type: { type: String, default: 'transaction' },
})

defineEmits(['close'])

const messages = {
  expense: { text: '¡Listo! Ya anoté tu gasto.', sub: 'Guardado' },
  income: { text: '¡Va! Tu plata ya está contada.', sub: 'Guardado' },
  transaction: { text: '¡Listo! Ya quedó.', sub: 'Guardado' },
  recurring: { text: 'Listo, ese pago se repite solo.', sub: 'Activo' },
  goal: { text: '¡Perfecto! Ya empezaste a ahorrar para eso.', sub: 'Meta creada' },
}

const message = computed(() => messages[props.type]?.text || '¡Listo!')
const submessage = computed(() => messages[props.type]?.sub || '')
</script>

<style scoped>
.done-confirmation { text-align: center; padding: var(--spacing-xl) 0; }

.done-icon { color: var(--color-success-500); margin-bottom: var(--spacing-md); }

.done-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-neutral-900);
  margin: 0 0 var(--spacing-sm);
}

.done-sub {
  font-size: 14px;
  color: var(--color-neutral-500);
  margin: 0 0 var(--spacing-lg);
}

.close-btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: var(--color-success-500);
  cursor: pointer;
}

.close-btn:hover { opacity: 0.9; }
</style>

<template>
  <div
    class="skeleton"
    :class="[
      'skeleton-' + variant,
      { 'skeleton-animated': animated }
    ]"
    :style="skeletonStyle"
    role="status"
    aria-label="Cargando..."
  >
    <span class="sr-only">Cargando...</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'text',
    validator: (v) => ['text', 'circle', 'rect', 'card', 'avatar'].includes(v)
  },
  width: { type: String, default: null },
  height: { type: String, default: null },
  animated: { type: Boolean, default: true },
})

const skeletonStyle = computed(() => ({
  width: props.width || undefined,
  height: props.height || undefined,
}))
</script>

<style scoped>
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
}

.skeleton-animated {
  animation: skeleton-shimmer 1.5s infinite linear;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-text {
  height: 1em;
  border-radius: 4px;
}

.skeleton-circle {
  border-radius: 50%;
}

.skeleton-rect {
  border-radius: 8px;
}

.skeleton-card {
  height: 120px;
  border-radius: 12px;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>

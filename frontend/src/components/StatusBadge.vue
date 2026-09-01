<template>
  <span
    class="status-badge"
    :class="variant"
  >
    <span
      v-if="dot"
      class="badge-dot"
    />
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'success', 'warning', 'error', 'info'].includes(v)
  },
  dot: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.status-badge.default {
  background: var(--color-neutral-100);
  color: var(--color-neutral-600);
}

.status-badge.success {
  background: var(--color-success-50);
  color: var(--color-success-700);
}

.status-badge.warning {
  background: var(--color-warning-50);
  color: var(--color-warning-700);
}

.status-badge.error {
  background: var(--color-error-50);
  color: var(--color-error-700);
}

.status-badge.info {
  background: var(--color-info-50);
  color: var(--color-info-600);
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: currentColor;
}
</style>

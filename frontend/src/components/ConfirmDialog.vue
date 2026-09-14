<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="confirm-overlay" @click="cancel" role="dialog" aria-modal="true" :aria-labelledby="titleId">
        <FocusTrap :visible="modelValue">
          <div class="confirm-content" @click.stop>
            <div class="confirm-icon" :class="'icon-' + type">
              <AlertTriangle v-if="type === 'danger'" :size="24" />
              <HelpCircle v-else-if="type === 'warning'" :size="24" />
              <Info v-else :size="24" />
            </div>
            <h3 :id="titleId" class="confirm-title">{{ title }}</h3>
            <p class="confirm-message">{{ message }}</p>
            <div class="confirm-actions">
              <button class="btn-cancel" @click="cancel" ref="cancelBtn">
                {{ cancelText }}
              </button>
              <button
                class="btn-confirm"
                :class="'btn-' + type"
                @click="confirm"
              :disabled="loading"
            >
              {{ loading ? 'Procesando...' : confirmText }}
            </button>
          </div>
        </div>
        </FocusTrap>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { AlertTriangle, HelpCircle, Info } from 'lucide-vue-next'
import FocusTrap from '@/components/FocusTrap.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmar' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: 'Confirmar' },
  cancelText: { type: String, default: 'Cancelar' },
  type: {
    type: String,
    default: 'info',
    validator: (v) => ['info', 'warning', 'danger'].includes(v)
  },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const titleId = `confirm-${Math.random().toString(36).slice(2, 9)}`
const cancelBtn = ref(null)

watch(() => props.modelValue, async (val) => {
  if (val) {
    await nextTick()
    cancelBtn.value?.focus()
  }
})

function confirm() {
  emit('confirm')
}

function cancel() {
  emit('update:modelValue', false)
  emit('cancel')
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.confirm-content {
  background: var(--color-neutral-0);
  border-radius: 16px;
  padding: 24px;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.confirm-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.icon-info {
  background: var(--color-info-50);
  color: var(--color-info-600);
}

.icon-warning {
  background: var(--color-warning-50);
  color: var(--color-warning-600);
}

.icon-danger {
  background: var(--color-error-50);
  color: var(--color-error-600);
}

  .confirm-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-neutral-900);
    margin-bottom: 8px;
  }

.confirm-message {
  color: var(--color-neutral-500);
  font-size: 0.9375rem;
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn-cancel {
  padding: 10px 20px;
  border-radius: 8px;
  font-family: var(--font-sans);
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: transform var(--transition-fast), background 150ms ease;
}

.btn-cancel {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
}

.btn-cancel:hover {
  background: var(--color-neutral-200);
}
.btn-cancel:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }

.btn-confirm {
  padding: 10px 20px;
  border-radius: 8px;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: all 150ms ease;
}

.btn-info {
  background: var(--color-info-600);
  color: var(--color-neutral-0);
}

.btn-info:hover {
  background: var(--color-primary-700);
}
.btn-info:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }

.btn-warning {
  background: var(--color-warning-600);
  color: var(--color-neutral-0);
}

.btn-warning:hover {
  background: var(--color-warning-700);
}
.btn-warning:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }

.btn-danger {
  background: var(--color-error-600);
  color: var(--color-neutral-0);
}

.btn-danger:hover {
  background: var(--color-error-700);
}
.btn-danger:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-confirm:active:not(:disabled) { transform: scale(0.97); filter: brightness(0.95); }

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

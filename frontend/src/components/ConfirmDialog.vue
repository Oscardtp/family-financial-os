<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="confirm-overlay" @click="cancel" role="dialog" aria-modal="true" :aria-labelledby="titleId">
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
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { AlertTriangle, HelpCircle, Info } from 'lucide-vue-next'

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
  background: white;
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
  background: #eff6ff;
  color: #2563eb;
}

.icon-warning {
  background: #fffbeb;
  color: #d97706;
}

.icon-danger {
  background: #fef2f2;
  color: #dc2626;
}

.confirm-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.confirm-message {
  color: #6b7280;
  font-size: 0.9375rem;
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: all 150ms ease;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-info {
  background: #2563eb;
  color: white;
}

.btn-info:hover {
  background: #1d4ed8;
}

.btn-warning {
  background: #d97706;
  color: white;
}

.btn-warning:hover {
  background: #b45309;
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-danger:hover {
  background: #b91c1c;
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

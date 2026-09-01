<template>
  <div class="confirm-backdrop" @click.self="$emit('cancel')">
    <div class="confirm-modal">
      <div class="confirm-icon">
        <Trash2 :size="28" />
      </div>
      <h3 class="confirm-title">¿Eliminar este evento?</h3>
      <p class="confirm-text">
        Se eliminará <strong>{{ title }}</strong> del calendario. Esta acción no se puede deshacer.
      </p>
      <div class="confirm-actions">
        <button class="btn-cancel" @click="$emit('cancel')">Cancelar</button>
        <button class="btn-delete" @click="$emit('confirm')" :disabled="loading">
          {{ loading ? 'Eliminando...' : 'Eliminar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Trash2 } from 'lucide-vue-next'

defineProps({
  title: { type: String, required: true },
  loading: { type: Boolean, default: false },
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 400;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.confirm-modal {
  background: #fff;
  border-radius: 16px;
  padding: 28px 24px 20px;
  width: 100%;
  max-width: 340px;
  text-align: center;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  animation: modalUp 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes modalUp {
  from { transform: scale(0.95) translateY(10px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

.confirm-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #fee2e2;
  color: #dc2626;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}

.confirm-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #141b1f;
  margin: 0 0 8px;
}

.confirm-text {
  font-size: 0.88rem;
  color: #536170;
  line-height: 1.45;
  margin: 0 0 20px;
}

.confirm-actions {
  display: flex;
  gap: 10px;
}

.btn-cancel {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 12px;
  background: #f2f2f2;
  color: #536170;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-delete {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 12px;
  background: #dc2626;
  color: #fff;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-delete:hover:not(:disabled) {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(220, 38, 38, 0.3);
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

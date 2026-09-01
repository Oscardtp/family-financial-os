<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="command-overlay"
      @click="close"
    >
      <div
        class="command-palette"
        @click.stop
      >
        <div class="command-input-wrapper">
          <Search
            :size="18"
            class="command-search-icon"
          />
          <input
            ref="inputRef"
            v-model="query"
            placeholder="Buscar acciones, navegar..."
            class="command-input"
            @keydown.escape="close"
            @keydown.down="highlightNext"
            @keydown.up="highlightPrev"
            @keydown.enter="executeHighlighted"
          >
          <kbd class="command-kbd">ESC</kbd>
        </div>

        <div
          v-if="filteredCommands.length > 0"
          class="command-results"
        >
          <div class="command-group">
            <span class="group-label">Navegacion</span>
            <div
              v-for="(cmd, index) in navigationCommands"
              :key="cmd.id"
              class="command-item"
              :class="{ highlighted: highlightedIndex === index }"
              @click="executeCommand(cmd)"
              @mouseenter="highlightedIndex = index"
            >
              <component
                :is="cmd.icon"
                :size="16"
                class="command-icon"
              />
              <span class="command-name">{{ cmd.name }}</span>
              <span
                v-if="cmd.shortcut"
                class="command-shortcut"
              >{{ cmd.shortcut }}</span>
            </div>
          </div>

          <div
            v-if="actionCommands.length > 0"
            class="command-group"
          >
            <span class="group-label">Acciones</span>
            <div
              v-for="(cmd, index) in actionCommands"
              :key="cmd.id"
              class="command-item"
              :class="{ highlighted: highlightedIndex === navigationCommands.length + index }"
              @click="executeCommand(cmd)"
              @mouseenter="highlightedIndex = navigationCommands.length + index"
            >
              <component
                :is="cmd.icon"
                :size="16"
                class="command-icon"
              />
              <span class="command-name">{{ cmd.name }}</span>
              <span
                v-if="cmd.shortcut"
                class="command-shortcut"
              >{{ cmd.shortcut }}</span>
            </div>
          </div>
        </div>

        <div
          v-else
          class="command-empty"
        >
          <p>Sin resultados para "{{ query }}"</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, LayoutDashboard, Receipt, CheckCircle, TrendingUp,
  Target, Plus, Bell, User, Users, Calendar,
  Download
} from 'lucide-vue-next'

const router = useRouter()
const isOpen = ref(false)
const query = ref('')
const highlightedIndex = ref(0)
const inputRef = ref(null)

const commands = [
  { id: 'nav-resumen', name: 'Resumen', icon: LayoutDashboard, action: () => router.push('/'), type: 'navigation' },
  { id: 'nav-debts', name: 'Mis Deudas', icon: Receipt, action: () => router.push('/debts'), type: 'navigation' },
  { id: 'nav-payments', name: 'Pagos', icon: CheckCircle, action: () => router.push('/payments'), type: 'navigation' },
  { id: 'nav-calendar', name: 'Calendario', icon: Calendar, action: () => router.push('/calendar'), type: 'navigation' },
  { id: 'nav-progress', name: 'Como Voy', icon: TrendingUp, action: () => router.push('/progress'), type: 'navigation' },
  { id: 'nav-goals', name: 'Metas', icon: Target, action: () => router.push('/goals'), type: 'navigation' },
  { id: 'nav-household', name: 'Mi Familia', icon: Users, action: () => router.push('/household'), type: 'navigation' },
  { id: 'nav-config', name: 'Mi Perfil', icon: User, action: () => router.push('/config'), type: 'navigation' },

  { id: 'action-new-debt', name: 'Nueva Deuda', icon: Plus, shortcut: 'N', action: () => router.push('/debts/new'), type: 'action' },
  { id: 'action-export', name: 'Exportar CSV', icon: Download, action: () => router.push('/transactions'), type: 'action' },
]

const filteredCommands = computed(() => {
  if (!query.value) return commands
  const q = query.value.toLowerCase()
  return commands.filter(cmd => cmd.name.toLowerCase().includes(q))
})

const navigationCommands = computed(() => filteredCommands.value.filter(cmd => cmd.type === 'navigation'))
const actionCommands = computed(() => filteredCommands.value.filter(cmd => cmd.type === 'action'))

const open = async () => {
  isOpen.value = true
  query.value = ''
  highlightedIndex.value = 0
  await nextTick()
  inputRef.value?.focus()
}

const close = () => {
  isOpen.value = false
  query.value = ''
}

const highlightNext = () => {
  if (highlightedIndex.value < filteredCommands.value.length - 1) {
    highlightedIndex.value++
  }
}

const highlightPrev = () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
  }
}

const executeHighlighted = () => {
  const cmd = filteredCommands.value[highlightedIndex.value]
  if (cmd) executeCommand(cmd)
}

const executeCommand = (cmd) => {
  cmd.action()
  close()
}

const handleKeydown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    if (isOpen.value) {
      close()
    } else {
      open()
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.command-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 20vh;
  z-index: 9999;
}

.command-palette {
  width: 100%;
  max-width: 560px;
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  border: 1px solid var(--color-neutral-200);
}

.command-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-neutral-200);
}

.command-search-icon {
  color: var(--color-neutral-400);
  flex-shrink: 0;
}

.command-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  color: var(--color-neutral-900);
  outline: none;
}

.command-input::placeholder {
  color: var(--color-neutral-400);
}

.command-kbd {
  font-size: 11px;
  padding: 2px 6px;
  background: var(--color-neutral-100);
  border-radius: var(--radius-sm);
  color: var(--color-neutral-500);
  font-family: var(--font-mono);
}

.command-results {
  max-height: 360px;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.command-group {
  margin-bottom: var(--spacing-sm);
}

.group-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-neutral-500);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--spacing-sm) var(--spacing-md);
}

.command-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.command-item:hover,
.command-item.highlighted {
  background: var(--color-neutral-100);
}

.command-icon {
  color: var(--color-neutral-500);
  flex-shrink: 0;
}

.command-name {
  flex: 1;
  font-size: 14px;
  color: var(--color-neutral-800);
}

.command-shortcut {
  font-size: 12px;
  padding: 2px 6px;
  background: var(--color-neutral-100);
  border-radius: var(--radius-sm);
  color: var(--color-neutral-500);
  font-family: var(--font-mono);
}

.command-empty {
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-neutral-500);
}

[data-theme="dark"] .command-palette {
  background: var(--color-neutral-100);
  border-color: var(--color-neutral-200);
}

[data-theme="dark"] .command-input {
  color: var(--color-neutral-100);
}

[data-theme="dark"] .command-item:hover,
[data-theme="dark"] .command-item.highlighted {
  background: var(--color-neutral-200);
}
</style>

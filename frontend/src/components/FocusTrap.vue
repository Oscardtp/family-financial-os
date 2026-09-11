<template>
  <div ref="container" :tabindex="-1" :aria-hidden="!visible">
    <slot v-if="visible" />
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  restoreFocus: { type: Boolean, default: true },
})

const container = ref(null)
let previousFocus = null

function getFocusableElements() {
  if (!container.value) return []
  return Array.from(
    container.value.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  ).filter(el => el.offsetParent !== null)
}

function handleKeydown(event) {
  if (!props.visible || !container.value) return
  if (event.key !== 'Tab') return

  const focusable = getFocusableElements()
  if (!focusable.length) return

  const first = focusable[0]
  const last = focusable[focusable.length - 1]

  if (event.shiftKey) {
    if (document.activeElement === first || !container.value.contains(document.activeElement)) {
      event.preventDefault()
      last.focus()
    }
  } else {
    if (document.activeElement === last || !container.value.contains(document.activeElement)) {
      event.preventDefault()
      first.focus()
    }
  }
}

watch(() => props.visible, async (newVal) => {
  if (newVal) {
    previousFocus = document.activeElement
    await nextTick()
    container.value?.focus()
  } else if (props.restoreFocus && previousFocus) {
    previousFocus.focus()
    previousFocus = null
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div ref="container" :tabindex="-1" :aria-hidden="!visible">
    <slot v-if="visible" />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  restoreFocus: { type: Boolean, default: true },
})

const container = ref(null)
let previousFocus = null

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
</script>

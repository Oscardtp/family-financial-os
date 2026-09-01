import { ref, onMounted, onUnmounted } from 'vue'

export function useAccessibility() {
  const isReducedMotion = ref(false)
  const isHighContrast = ref(false)
  const isScreenReader = ref(false)

  onMounted(() => {
    if (typeof window !== 'undefined') {
      isReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      isHighContrast.value = window.matchMedia('(prefers-contrast: high)').matches
      isScreenReader.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches &&
        !window.matchMedia('(hover: hover)').matches

      const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      const contrastQuery = window.matchMedia('(prefers-contrast: high)')

      motionQuery.addEventListener('change', (e) => {
        isReducedMotion.value = e.matches
      })

      contrastQuery.addEventListener('change', (e) => {
        isHighContrast.value = e.matches
      })
    }
  })

  function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), ' +
      'input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    const firstFocusable = focusableElements[0]
    const lastFocusable = focusableElements[focusableElements.length - 1]

    function handleTab(e) {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus()
          e.preventDefault()
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus()
          e.preventDefault()
        }
      }
    }

    element.addEventListener('keydown', handleTab)
    firstFocusable?.focus()

    return () => {
      element.removeEventListener('keydown', handleTab)
    }
  }

  function announceToScreenReader(message, priority = 'polite') {
    const announcer = document.createElement('div')
    announcer.setAttribute('aria-live', priority)
    announcer.setAttribute('aria-atomic', 'true')
    announcer.className = 'sr-only'
    announcer.textContent = message
    document.body.appendChild(announcer)

    setTimeout(() => {
      document.body.removeChild(announcer)
    }, 1000)
  }

  function generateId(prefix = 'el') {
    return `${prefix}-${Math.random().toString(36).slice(2, 9)}`
  }

  function getAriaProps(options = {}) {
    const props = {}
    if (options.label) props['aria-label'] = options.label
    if (options-describedby) props['aria-describedby'] = options-describedby
    if (options-labelledby) props['aria-labelledby'] = options-labelledby
    if (options.expanded !== undefined) props['aria-expanded'] = options.expanded
    if (options.hidden !== undefined) props['aria-hidden'] = options.hidden
    if (options.live) props['aria-live'] = options.live
    if (options.atomic !== undefined) props['aria-atomic'] = options.atomic
    if (options.role) props['role'] = options.role
    return props
  }

  return {
    isReducedMotion,
    isHighContrast,
    isScreenReader,
    trapFocus,
    announceToScreenReader,
    generateId,
    getAriaProps,
  }
}

import { ref, computed } from 'vue'

export function useFormattedNumber(initialValue = 0, options = {}) {
  const { prefix = '$', decimals = 0 } = options

  const rawValue = ref(initialValue)

  function formatNumber(num) {
    if (num === null || num === undefined || num === '') return prefix ? prefix + ' 0' : '0'
    const n = Number(num)
    if (isNaN(n)) return prefix ? prefix + ' 0' : '0'
    const parts = n.toFixed(decimals).split('.')
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.')
    const formatted = parts.join(',')
    return prefix ? prefix + ' ' + formatted : formatted
  }

  const displayValue = computed(() => formatNumber(rawValue.value))

  function onInput(event) {
    const input = event.target
    let val = input.value
    const hasPrefix = prefix && val.startsWith(prefix)
    if (hasPrefix) {
      val = val.substring(prefix.length).trim()
    }
    val = val.replace(/[^0-9]/g, '')
    if (val === '') {
      rawValue.value = 0
      input.value = prefix ? prefix + ' 0' : '0'
      return
    }
    const num = parseInt(val, 10)
    rawValue.value = num
    input.value = formatNumber(num)
    const len = input.value.length
    input.setSelectionRange(len, len)
  }

  function onFocus(event) {
    const input = event.target
    const len = input.value.length
    input.setSelectionRange(len, len)
  }

  function setInitial(value) {
    rawValue.value = Number(value) || 0
  }

  return { rawValue, displayValue, onInput, onFocus, setInitial, formatNumber }
}

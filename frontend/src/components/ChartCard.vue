<template>
  <div class="chart-wrapper">
    <canvas ref="canvas" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  type: { type: String, required: true },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) },
})

const canvas = ref(null)
let chartInstance = null

function createChart() {
  if (chartInstance) chartInstance.destroy()
  if (!canvas.value) return
  chartInstance = new Chart(canvas.value, {
    type: props.type,
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      ...props.options,
    },
  })
}

onMounted(createChart)
watch(() => props.data, createChart, { deep: true })
onBeforeUnmount(() => { if (chartInstance) chartInstance.destroy() })
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
}
</style>

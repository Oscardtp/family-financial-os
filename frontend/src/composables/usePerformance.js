const performanceMetrics = {
  marks: {},
  measures: [],
}

export function usePerformance() {
  function mark(name) {
    if (typeof performance !== 'undefined') {
      performance.mark(name)
      performanceMetrics.marks[name] = performance.now()
    }
  }

  function measure(name, startMark, endMark) {
    if (typeof performance !== 'undefined') {
      try {
        performance.measure(name, startMark, endMark)
        const entries = performance.getEntriesByName(name)
        const duration = entries[entries.length - 1]?.duration || 0
        performanceMetrics.measures.push({ name, duration, timestamp: Date.now() })
        return duration
      } catch (e) {
        console.warn('Performance measure failed:', e)
        return 0
      }
    }
    return 0
  }

  function getMetrics() {
    return { ...performanceMetrics }
  }

  function logSlowOperations(threshold = 1000) {
    const slow = performanceMetrics.measures.filter(m => m.duration > threshold)
    if (slow.length > 0) {
      console.warn('Slow operations detected:', slow)
    }
    return slow
  }

  function clearMetrics() {
    performanceMetrics.marks = {}
    performanceMetrics.measures = []
    if (typeof performance !== 'undefined') {
      performance.clearMarks()
      performance.clearMeasures()
    }
  }

  function onLCP(callback) {
    if (typeof PerformanceObserver !== 'undefined') {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries()
          const lastEntry = entries[entries.length - 1]
          if (!lastEntry) return
          callback(lastEntry.startTime)
        })
        observer.observe({ type: 'largest-contentful-paint', buffered: true })
        return () => observer.disconnect()
      } catch (e) {
        console.warn('LCP observer not supported')
      }
    }
    return () => {}
  }

  function onFID(callback) {
    if (typeof PerformanceObserver !== 'undefined') {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries()
          entries.forEach(entry => {
            if (!entry || entry.startTime == null) return
            callback(entry.processingStart - entry.startTime)
          })
        })
        observer.observe({ type: 'first-input', buffered: true })
        return () => observer.disconnect()
      } catch (e) {
        console.warn('FID observer not supported')
      }
    }
    return () => {}
  }

  function onCLS(callback) {
    if (typeof PerformanceObserver !== 'undefined') {
      try {
        let clsValue = 0
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach(entry => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value
              callback(clsValue)
            }
          })
        })
        observer.observe({ type: 'layout-shift', buffered: true })
        return () => observer.disconnect()
      } catch (e) {
        console.warn('CLS observer not supported')
      }
    }
    return () => {}
  }

  return {
    mark,
    measure,
    getMetrics,
    logSlowOperations,
    clearMetrics,
    onLCP,
    onFID,
    onCLS,
  }
}

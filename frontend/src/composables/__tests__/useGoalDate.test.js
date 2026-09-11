import { describe, it, expect } from 'vitest'
import { calcularFechaObjetivo } from '@/composables/useGoalDate'

describe('calcularFechaObjetivo', () => {
  it('devuelve null cuando montoObjetivo es nulo', () => {
    expect(calcularFechaObjetivo(null, 100000)).toBeNull()
  })

  it('devuelve null cuando aporteMensual es nulo', () => {
    expect(calcularFechaObjetivo(1000000, null)).toBeNull()
  })

  it('devuelve null cuando ambos valores son undefined', () => {
    expect(calcularFechaObjetivo(undefined, undefined)).toBeNull()
  })

  it('devuelve null cuando montoObjetivo es <= 0', () => {
    expect(calcularFechaObjetivo(0, 100000)).toBeNull()
    expect(calcularFechaObjetivo(-500000, 100000)).toBeNull()
  })

  it('devuelve null cuando aporteMensual es <= 0', () => {
    expect(calcularFechaObjetivo(1000000, 0)).toBeNull()
    expect(calcularFechaObjetivo(1000000, -100000)).toBeNull()
  })

  it('devuelve null cuando montoObjetivo es Infinity o NaN', () => {
    expect(calcularFechaObjetivo(Infinity, 100000)).toBeNull()
    expect(calcularFechaObjetivo(NaN, 100000)).toBeNull()
  })

  it('devuelve null cuando aporteMensual es Infinity o NaN', () => {
    expect(calcularFechaObjetivo(1000000, Infinity)).toBeNull()
    expect(calcularFechaObjetivo(1000000, NaN)).toBeNull()
  })

  it('devuelve null cuando el cálculo de meses desborda el rango de Date', () => {
    expect(calcularFechaObjetivo(1e18, 1)).toBeNull()
  })

  it('calcula meses exactos con Math.ceil y retorna fecha formateada', () => {
    const result = calcularFechaObjetivo(5000000, 200000)
    expect(result).not.toBeNull()
    expect(result.meses).toBe(25)
    expect(result.warning).toBe('')
    expect(typeof result.fechaObjetivo).toBe('string')
    expect(result.fechaObjetivo.length).toBeGreaterThan(0)
  })

  it('redondea los meses hacia arriba usando Math.ceil', () => {
    const result = calcularFechaObjetivo(1000000, 300000)
    expect(result.meses).toBe(4)
  })

  it('formatea la fecha en español colombiano (día de mes de año)', () => {
    const result = calcularFechaObjetivo(1200000, 100000)
    expect(result.fechaObjetivo).toMatch(/\d{1,2} de \w+ de \d{4}/)
  })

  it('muestra advertencia cuando los meses exceden 120', () => {
    const result = calcularFechaObjetivo(1000000000, 100000)
    expect(result.meses).toBe(10000)
    expect(result.warning).not.toBe('')
    expect(result.warning).toMatch(/10 años/)
  })

  it('no muestra advertencia cuando los meses son 120 o menos', () => {
    const result = calcularFechaObjetivo(120000000, 1000000)
    expect(result.meses).toBe(120)
    expect(result.warning).toBe('')
  })

  it('retorna meses correctos en el límite exacto de 121', () => {
    const result = calcularFechaObjetivo(121000000, 1000000)
    expect(result.meses).toBe(121)
    expect(result.warning).not.toBe('')
  })

  it('acepta strings numéricos como entrada', () => {
    const result = calcularFechaObjetivo('5000000', '200000')
    expect(result).not.toBeNull()
    expect(result.meses).toBe(25)
  })
})

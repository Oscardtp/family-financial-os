# 004 — Representación del Dinero

- **Estado:** Aceptada
- **Fecha:** 2026-08-11

## Contexto

El motor financiero requiere exactitud decimal. `float`/`number` produce errores de redondeo
que en dinero son inaceptables (pérdidas/ganancias fantasma).

## Decisión

Almacenar y operar importes en **unidades menores** (centavos) usando `bigint`, con **Dinero.js
v2.0.2** como VO puro (`Money = { amount: bigint, currency: string }`).

Reglas:
- No se suman `Money` de distinta moneda (`CurrencyMismatchError`).
- Conversión a `number`/float solo para presentación, nunca para cálculo.
- Redondeos con `ROUND_HALF_EVEN` sobre centavos.

## Consecuencias

- ✅ Exactitud garantizada por tipo (`bigint`).
- ✅ Dinero.js v2 (bigint) encaja con `bigint` de PostgreSQL → no hay conversión peligrosa.
- ❌ Código de presentación debe convertir (responsabilidad aislada en *Money*).

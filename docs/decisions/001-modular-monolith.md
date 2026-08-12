# 001 — Modular Monolith

- **Estado:** Aceptada
- **Fecha:** 2026-08-11

## Contexto

Necesitamos un backend financiero que evolucione rápido (familia) pero que no nos encierre en
microservicios complejos desde el día uno. La arquitectura debe soportar luego un cliente Web,
Mobile, y un asistente IA + gemelo financiero.

## Decisión

Arquitectura **Modular Monolith** con **Clean Architecture**: un solo artefacto desplegable,
organizado en *bounded contexts* (modules) con capas bien aisladas (`api`, `modules`,
`infrastructure`, `shared`). Las reglas ver: `.ai/architecture-rules.md`.

## Consecuencias

- ✅ Despliegue simple, tests unitarios puros, refactorizaciones locales.
- ✅ Cada módulo financiero (accounts, transactions, budgets, goals, net-worth) puede extraerse
      a microservicio más adelante (doble entrada de límites de contexto).
- ❌ Acoplamiento físico (BD única) — aceptable para fase familiar.

# Project Context — Family Financial OS

## Propósito

Family Financial OS es un **Sistema Operativo Financiero Familiar**: una plataforma para que un
hogar entienda e administre integralmente su economía, más allá de un simple gestor de gastos.

Se basa en cuatro conceptos fundamentales:

1. **Patrimonio** — qué posee y qué debe la famila.
2. **Flujo** — cómo entra y sale el dinero.
3. **Compromisos** — obligaciones futuras (gastos recurrentes, deudas, metas).
4. **Decisiones** — impacto de un cambio financiero ("¿qué pasa si…?").

## Alcance actual (esta fase)

**Backend / Financial Core.** No se desarrolla frontend en esta fase. El backend quedará preparado
para ser consumido por: aplicación Web, aplicación Mobile, y futuramente un asistente financiero IA y un
gemelo financiero digital.

## Stack (confirmado)

| Capa | Tecnología | Versión (stable, verificada) |
|------|------------|------------------------------|
| Runtime | Node.js | v24.18 |
| Framework | Next.js | 16.3.0 (App Router) |
| UI (futuro) | React | 19.2.8 |
| Lenguaje | TypeScript | 5.9.3 (alineado a Next 16) |
| ORM | Prisma | 7.9.1 |
| DB | PostgreSQL | 17.10 (local dev) / Supabase (prod) |
| Validación | Zod | 4.4.3 (v4) |
| Testing | Vitest | 4.1.10 (+ Playwright en fases posteriores) |
| Lint/Format | ESLint 9 / Prettier | 3.9.6 |
| Auth | Supabase Auth | @supabase/supabase-js 2.112.3 + @supabase/ssr 0.12.4 |
| Dinero (engine puro) | Dinero.js | 2.0.2 (bigint) |

## Decisiones arquitectónicas clave (ver ADRs en docs/decisions/)

- ADR-001: Modular Monolith (no microservicios).
- ADR-002: PostgreSQL como única DB (local portable para dev; Supabase para prod).
- ADR-003: Prisma como capa de acceso a PostgreSQL + singleton global.
- ADR-004: Dinero en unidades menores con `bigint` (Dinero.js v2), nunca `float`.
- ADR-005: Selección de Agent Skills (ver .ai/skills-registry.md).

## Reglas de prioridad

```
CORRECCIÓN FINANCIERA > SIMPLICIDAD > MANTENIBILIDAD > ESCALABILIDAD PREMATURA
```

## Próximo paso

Completar el bootstrap técnico (dependencias, schema, migración, cliente Prisma, tests puro,
docs, git) y reportar antes de pasar a implementar el dominio financiero.

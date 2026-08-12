# 006 — UUID v7 como clave primaria

- **Estado:** Aceptada
- **Fecha:** 2026-08-12

## Contexto

Los IDs deben ser **cronológicos** (útiles para indexado, conciliación, debugging) y no revelar
volumen exacto. UUID v4 es aleatorio (no cronológico). Se valora usar UUID v7.

## Decisión

Usar **Prisma 7 PSL `@default(uuid(7))`** para todas las PK (`id String @id @default(uuid(7))`):
- `uuid(7)` es el tipo v7 de timestamps.
- En Prisma 7 el UUID se genera **cliente-side** (el `column_default` de Postgres queda vacío),
  por lo que no se crea `DEFAULT` en la DB — el cliente lo inyecta en el INSERT.

Verificado: smoke test `prisma.smoke.test.ts` crea un `Transaction` sin `id` y obtiene un UUID v7
(v7 confirmed: nibble de versión `7`, variante `8/9/a/b`).

## Evidencia

`firecrawl developer-index` → docs PSL `uuid()`: "Generate `uuid(7)` values as IDs using UUID v7".

## Alternativas descartadas

- `@default(uuid())` (v4): cronológico = no. Se usaba inicialmente; reemplazado por v7.
- `gen_random_uuid_v7()` DB-side: PostgreSQL 17 **no** expone una función v7 nativa fiable → se
  prefiere generación cliente-side de Prisma.
- `bigserial`/`ULID`: requieren más infra; no nativo de Prisma.

## Consecuencias

- ✅ IDs cronológicos → mejor rendimiento de indexado (R6).
- ✅ Sin función DB extra; cliente-side, coherente con Prisma 7 rust-free.
- ❌ Las PK se generan en el cliente (no en DB) — aceptable; riesgo de colisión prácticamente nulo.

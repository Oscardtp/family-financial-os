# 002 — PostgreSQL

- **Estado:** Aceptada
- **Fecha:** 2026-08-11

## Contexto

La app maneja dinero, conciliación bancaria y datos financieros estructurados que requieren
transacciones ACID y consistencia fuerte.

## Decisión

**PostgreSQL 17** como única base de datos. En desarrollo se corre un PostgreSQL local (portable,
sin instalador) en `localhost:5432`; en producción/compartida se usa **Supabase Postgres**
(proporcionar `DATABASE_URL`). La schema es idéntica en ambos (no hay vendor lock-in de funcionalidad).

## Consecuencias

- ✅ ACID para el double-entry; tipos `bigint`/UUID v7 nativos; consistencia fuerte.
- ✅ SQL estándar: migraciones reproducibles con Prisma.
- ✅ Local dev sin Supabase → migraciones y tests pueden correr offline.
- ❌ Necesidad de un cliente SQL local para dev (resuelto con binarias portable de PG 17).

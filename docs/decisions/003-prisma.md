# 003 — Prisma 7 + Singleton Client (driver adapter)

- **Estado:** Aceptada
- **Fecha:** 2026-08-12 (actualizada para Prisma ORM v7)

## Contexto

Prisma 7 es *rust-free*: `datasource.url` se eliminó del schema y el cliente runtime requiere un
driver adapter para conexión directa a Postgres. También se quiere evitar múltiples instancias
de `PrismaClient` en dev (HMR de Next.js) — fuga de conexiones.

## Decisión

Usar **Prisma 7.9.1** con:

1. `prisma.config.ts` (root) como única fuente de la connection URL para CLI/migrate:
```ts
import "dotenv/config";
import { defineConfig, env } from "prisma/config";
export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: { path: "prisma/migrations" },
  datasource: { url: env("DATABASE_URL") },
});
```
2. `schema.prisma`: `datasource db { provider = "postgresql" }` (**sin `url`**).
3. Cliente runtime con **driver adapter `PrismaPg`** (`@prisma/adapter-pg` + `pg`), en un
   **singleton global** HMR-safe (`src/infra/database/prisma.ts`):
```ts
import { PrismaClient } from "@prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
declare global { var prisma: PrismaClient | undefined }
function createClient() {
  return new PrismaClient({ adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL! }) });
}
const client = global.prisma ?? createClient();
if (process.env.NODE_ENV !== "production") global.prisma = client;
export default client;
```
4. Repositorios del dominio exponen **interfaces**; `infrastructure/repositories` las implementa con
   Prisma (inyección en use-cases).

## Evidencia

Verificado con `firecrawl developer-index` (primary sources):
- Prisma docs (`prisma-config-reference`): `datasource.url` → `prisma.config.ts`; `directUrl`/`adapter`/`engine`/`studio` **removed** en v7.
- issue `prisma/prisma#17566`: el singleton evita fugas de conexiones en HMR.
- issue `prisma/prisma#29252` + docs: Postgres directo usa el adapter **`PrismaPg`** (v7 rust-free).

## Consecuencias

- ✅ Conexión única por proceso; compatible Prisma 7 + Next 16 + Postgres 17.
- ✅ CLI (migrate/dev/studio) y runtime (PrismaClient) configurados de forma coherente.
- ✅ Repositorios testeables (interface → mock).
- ❌ El singleton global en dev (aceptado; prod crea una instancia).
- ❌ Requiere `@prisma/adapter-pg` + `pg` (dependencias de runtime añadidas).

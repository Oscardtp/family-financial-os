# 005 — Agent Skills

- **Estado:** Aceptada
- **Fecha:** 2026-08-11

## Contexto

El agente que mantendrá y evolucionará Family Financial OS necesita acceso a búsqueda web,
extracción de contenido y —crucial para no cometer errores técnicos— resolución de dudas de
implementación contra fuentes primarias (issues/PRs/docs oficiales). El entorno es Windows.

## Decisión

Seleccionar el catálogo de Firecrawl + la skill de PowerShell Windows, evaluando 28 skills
ver el **`.ai/skills-registry.md`** (tabla de evaluación completa: 28 items).

**Instaladas / activas:**
1. `powershell-windows` — scripting local correcto en Windows.
2. `firecrawl-developer-index` — dev Qs con fuentes primarias (verificada operativa: resolvió
   el patrón Prisma Client singleton desde docs.prisma.io + prisma/prisma#17566).
3. `firecrawl-search` — research web + extracción full-page.

**Rechazadas** (out of scope / no son features del producto): `firecrawl-build*`,
`firecrawl-company-directories`, `firecrawl-competitive-intel`, `firecrawl-lead-gen`,
`firecrawl-lead-research`, `firecrawl-seo-audit`, `firecrawl-shop`, `firecrawl-website-design-clone`,
`firecrawl-knowledge-ingest`.

**Opcionales** (casos puntuales): `firecrawl-crawl`, `firecrawl-download`, `firecrawl-deep-research`,
`firecrawl-interact`, `firecrawl-qa`, `firecrawl-market-research`, `firecrawl-monitor`,
`firecrawl-parse`, `firecrawl-blog`, `firecrawl-demo-walkthrough`, `firecrawl-dashboard-reporting`,
`firecrawl-research-papers`, `firecrawl-research-index`, `customize-opencode`.

## Consecuencias

- ✅ Las decisiones técnicas se verifican con fuentes primarias (menos errores de versión).
- ✅ El runtime de Windows se maneja sin bugs de path/quoting.
- ✅ No hay dependencias innecesarias del producto (las `firecrawl-build-*` no se integran al app).

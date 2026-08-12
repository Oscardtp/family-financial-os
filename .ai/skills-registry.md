# Skills Registry

Catálogo de **Agent Skills** evaluadas, seleccionadas e instaladas para este repositorio.

> Las skills son extensiones del agente que se invocan vía la CLI `firecrawl` (v1.19.29) o el
> runtime de opencode. Se listan en este registro y se documenta cuándo usar cada una.

## Tabla de evaluación

| # | Skill | Categoría | Uso típico | INSTALAR/OPCIONAL/RECHAZAR | Justificación |
|---|-------|-----------|------------|----------------------------|---------------|
| 1 | `firecrawl-search` | Research | "buscar X en la web y leer contenido completo" | **INSTALAR** | Búsqueda + extracción full-page; base de todo research. |
| 2 | `firecrawl-developer-index` | Dev Qs | "resolver dudas técnicas con fuentes primarias" | **INSTALAR** | Verificada aquí: confirmó el patrón Prisma Client singleton desde docs.prisma.io + issue prisma/prisma#17566. Evita errores de implementación. |
| 3 | `firecrawl-deep-research` | Research | "informe analítico riguroso sobre un tema" | **OPCIONAL** | Solo si se necesita un reporte formal/citable. No es CRUD; usar con moderación. |
| 4 | `firecrawl-company-directories` | Data | "extraer listas de empresas/directorios" | **RECHAZAR** | No hay necesidad de scrapear directorios de empresas en un OS familiar. |
| 5 | `firecrawl-competitive-intel` | Data | "monitor de precios/feats de competidores" | **RECHAZAR** | Producto B2C familiar; no hay competidores que monitorizar con scrapping. |
| 6 | `firecrawl-crawl` | Data | "extraer todo un sitio/docs" | **OPCIONAL** | Útil para descargar specs de APIs/estándares (Open Banking, ISO 20022) una vez. |
| 7 | `firecrawl-download` | Data | "guardar docs para uso offline" | **OPCIONAL** | Descargar specs ISO/open-banking offline. Caso puntual. |
| 8 | `firecrawl-knowledge-base` | Data | "construir corpus/know-how" | **OPCIONAL** | Si se quiere un corpus de docs regulatorios (Open Banking España). |
| 9 | `firecrawl-knowledge-ingest` | Data | "docs portales login/gated" | **RECHAZAR** | No hay docs gated relevantes por ahora. |
| 10 | `firecrawl-lead-gen` | Data | "generar listas de prospección" | **RECHAZAR** | No es funnel de ventas. |
| 11 | `firecrawl-lead-research` | Research | "brief previo a reunión/sales" | **RECHAZAR** | No es sales. |
| 12 | `firecrawl-market-research` | Research | "métricas de mercado/finanzas" | **OPCIONAL** | Potencial: datos de tipos de interés, inflación, referencias para simulaciones. |
| 13 | `firecrawl-monitor` | Monitor | "alertas cuando X cambia" | **OPCIONAL** | Útil para monitorizar tipos de cambio/benchmark o docs de versión de Next/Prisma. |
| 14 | `firecrawl-parse` | Local | "parsear PDFs/DOCX locales" | **OPCIONAL** | Si el engine debe ingerir extractos de banco PDF. |
| 15 | `firecrawl-qa` | QA | "tests exploratorios de sitios" | **OPCIONAL** | QA de la web cuando exista. |
| 16 | `firecrawl-research-papers` | Research | "literatura/papers técnicos" | **OPCIONAL** | Si se usan modelos de depreciación/interest formal. |
| 17 | `firecrawl-research-index` | Research | "encontrar papers que respondan X" | **OPCIONAL** | Ver arriba: usar con moderación. |
| 18 | `firecrawl-seo-audit` | SEO | "auditoría SEO web" | **RECHAZAR** | No es web-first todavía. |
| 19 | `firecrawl-shop` | Shopping | "comparar productos" | **RECHAZAR** | No es e-commerce. |
| 20 | `firecrawl-website-design-clone` | Design | "extraer sistema de diseño" | **OPCIONAL** | Solo cuando se diseñe la web. |
| 21 | `firecrawl-dashboard-reporting` | Data | "extraer métricas de dashboards" | **OPCIONAL** | Si se conecta a APIs de bancos con dashboards. |
| 22 | `firecrawl-demo-walkthrough` | UX | "walkthrough UX de un producto" | **OPCIONAL** | Benchmarking UX de apps financieras. |
| 23 | `firecrawl-interact` | Interact | "clicks/forms/login en páginas" | **OPCIONAL** | Para probar flows de auth bancaria/oauth. |
| 24 | `firecrawl-build` | Build | "integrar fetch/scrape en el código app" | **RECHAZAR** | El OS no consume contenido web como feature; sería dependencia innecesaria. |
| 25 | `firecrawl-build-scrape/-search/-interact` | Build | "integrar /scrape /search /interact en app" | **RECHAZAR** | Ver fila 24: no son features del producto. |
| 26 | `firecrawl-build-onboarding` | Build | "setup creds Firecrawl app" | **RECHAZAR** | No integramos Firecrawl en el producto. |
| 27| `firecrawl-build-interact` | Build | "interacciones multi-step en app" | **RECHAZAR** | No es feature del producto. |
| 28| `powershell-windows` | Windows | "patrones PS5.1 Windows" | **INSTALAR** | Entorno Windows; esta skill evita errores de path/quoting/cmdlet cuando corrremos scripts locales (p. ej. arrancar PG portable). |
| 29| `customize-opencode` | Meta | "editar opencode.json/.opencode" | **OPCIONAL** | Solo si se customiza la configuración del agente (no es necesario todavía). |

## Skills activas (instaladas / cargadas)

1. `powershell-windows` — cargada (ver `powershell-windows` skill). Uso: scripting local correcto en Windows.
2. `firecrawl-developer-index` — cargada + verificada funcionando (CLI `firecrawl developer "query"`). Uso: resolver dudas técnicas con fuentes primarias.
3. `firecrawl-search` — disponible. Uso: research general con extracción de página.

## Cómo invocar

- **`firecrawl developer "<query>"`** — developer-index (fuentes: GitHub issues/PRs, docs oficiales, READMEs).
  Ejemplo: `npx firecrawl developer "prisma client singleton nextjs 16 route handlers"`.
- **`firecrawl search "<query>"`** — web search + extracción.
- Las skills también se pueden cargar en tiempo de conversación vía la herramienta `skill` del agente.

## Criterio de decisón de skills

> **Solo herramientas que reduzcan riesgo o coste de este proyecto particular.**
> Se **rechazan** por: no ser features del producto (`firecrawl-build-*`), o fuera de scope
> (SEO, lead-gen, e-commerce, directorios de empresas). Se marcan **OPCIONAL** si son casos
> puntuales (papers, specs regulatorias).

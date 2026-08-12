<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

<!-- BEGIN:family-financial-os-agent-rules -->
# Family Financial OS — Project Rules

The canonical agent memory lives in `.ai/` (read-first): `project-context.md`,
`technology-stack.md`, `architecture-rules.md`, `domain-rules.md`, `current-state.md`,
`skills-registry.md`. Architectural decisions are recorded as ADRs in `docs/decisions/`.

## Quick facts
- Stack in this repo: Node 24 · Next.js 16 (App Router) · React 19 · TypeScript 5.9 · Prisma 7 · PostgreSQL 17/Supabase · Zod 4 · Dinero.js v2 · Vitest.
- Environment: Windows 11 PowerShell 5.1. The `powershell-windows` skill is active; use `cmd /c md` / `New-Item -ItemType Directory -Force -Path a,b` for multi-path creation and quote paths with spaces.

## Agent Skills (selected — see `.ai/skills-registry.md`)
- `firecrawl-developer-index` (INSTALLED): resolve technical/dev questions against primary sources (docs/GitHub issues/PRs). Invoke via `npx firecrawl developer "<query>"`.
- `firecrawl-search` (INSTALLED): web search + full-page extraction.
- `powershell-windows` (INSTALLED): correct Windows PowerShell scripting.

## Workflow
1. Before changing architecture/tech, record (or update) an ADR in `docs/decisions/` and the relevant `.ai/*.md`.
2. Verify dev claims with `firecrawl developer-index` (primary sources) before implementing version-sensitive code (e.g. Prisma singleton, Next 16 App Router API).
3. Lint & typecheck before finishing: `npm run lint`, `npx tsc --noEmit`.
4. Test pure domain: `npm test` (Vitest). DB integration tests are deferred until Postgres is running.

## Non-goals of this phase (do NOT build yet)
- API routes, database schema/migrations, Financial Engine, frontend, and full authentication plumbing are OUT OF SCOPE for the agent-skills task — they are tracked as pending in `.ai/current-state.md`.
<!-- END:family-financial-os-agent-rules -->

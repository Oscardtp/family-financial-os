# AGENTS.md — Contrato de Comportamiento

## 1. 🚨 Estado Operativo Actual

```
MODO: BASELINE ESTABLE (post-FASE 6.2.1)
CHECKPOINT: d21a87d — "fix(budget): eliminate intermediate step in budget creation flow (FASE 6.2.1)"
```

**Restricción temporal:** No desarrollar nuevas funcionalidades financieras hasta completar todas las fases del Protocolo Maestro (Fase 0 a Fase 6). Leer `docs/PROTOCOLO_MAESTRO.md` antes de asumir el estado actual.

**Prioridad:** Estabilidad > Features. Cualquier cambio debe preservar el baseline verificado.

---

## 2. 🛑 Reglas Absolutas

**NUNCA ejecutar sin autorización explícita:**

| Categoría | Acciones prohibidas |
|-----------|-------------------|
| **Base de Datos** | `DROP`, `TRUNCATE`, `DELETE` masivo, `ALTER TABLE` manual, `alembic upgrade/downgrade/stamp` sobre DB real, recrear DB, modificar datos existentes fuera de un procedimiento explícitamente autorizado y validado |
| **Git** | `git reset --hard`, `git clean -fd`, `git checkout -- .`, `git restore .`, `git branch -D`, `git push --force` |
| **Secrets** | Hardcodear credenciales, imprimir passwords/tokens/connection strings, incluir `.env` en commits |
| **Backups** | Eliminar, modificar, o incluir en Git. Protegidos por `.gitignore` |
| **Alcance** | Refactors, limpiezas, actualizaciones de dependencias no relacionadas con la tarea actual |

**Consecuencia:** Si alguna acción parece necesaria → **DETENERSE** y reportar como `BLOCKED`.

**Regla de datos:** La DB contiene datos familiares reales. Código puede reconstruirse. Datos reales pueden no recuperarse.

---

## 3. 🧠 Contexto del Proyecto

### Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| Frontend | Vue.js 3 (Composition API), Pinia, Vue Router, Vite, Chart.js |
| DB | PostgreSQL 16 (producción) + SQLite (desarrollo) |
| Auth | JWT (python-jose), bcrypt, passlib |
| Testing | pytest, pytest-asyncio, httpx (backend) / Vitest (frontend) |
| Deploy | Docker, docker-compose |
| Moneda | COP (pesos colombianos) |

### Arquitectura

- **Clean Architecture:** domain → application → infrastructure → presentation
- **Multi-tenant:** Todo acceso por `household_id`. Roles: Owner/Member/Viewer
- **Money VO:** `Decimal` con cuantización a 2 decimales. **NUNCA** `float`
- **InterestRate engine:** `RateEngine.to_monthly_rate(InterestRate)` en `backend/app/financial_engine/rate_engine.py`. Nunca `/1200` ni fórmulas inline
- **RateType enum:** `EA`, `EM`, `NOMINAL`, `DAILY`. Default = `EA`

### Convenciones de Negocio

- **Idioma:** Español (lenguaje colombiano natural)
- **Timezone:** America/Bogota (UTC-5)
- **Calendario único:** El proyecto tiene pantalla Calendario dedicada. No duplicar en otras vistas
- **Responsive:** Toda UI debe funcionar en mobile y desktop
- **Presupuesto único:** `BudgetDetailModal` es el único centro de gestión del presupuesto. Cualquier funcionalidad futura (health_score, distribución 50/30/20, recomendaciones inteligentes, historial de cambios) se integra dentro de ese mismo flujo. No crear nuevos modales ni pantallas paralelas para presupuesto

### Frontend — Trampas Conocidas

- `useFormattedNumber`: `onInput` y `onFocus` requieren el evento nativo. Sin evento → `TypeError`
- `Debts.vue`: Usar `Number(...)` para coerción al sumar desde API. Sin coerción → `NaN`
- `rate_type` selector: Mantener sincronizado con backend enum. Labels: "Tasa Interés" (no "Tasa Mensual")

---

## 4. 🔄 Flujos de Trabajo (SOPs)

### Antes de Cualquier Tarea

```
1. git status          ← Estado actual
2. Diagnosticar        ← Causa raíz, NO fixear sin diagnosticar
3. Plan mínimo         ← 1 problema → 1 causa → 1 cambio pequeño
4. Implementar         ← Código + tests
5. Verificar           ← git diff, tests pass
6. Reportar             ← STATUS: PASS/FAIL/BLOCKED
```

### Nuevo Endpoint FastAPI

```
1. test-driven-development    ← Test fallido primero
2. python-testing              ← Fixtures, parametrize
3. fastapi-patterns            ← DI, auth, service layer, response_model
4. python-patterns             ← Código idiomático
5. security-review             ← Checklist post-implementación
```

### Migración de DB

```
1. postgres-patterns           ← Tipos, índices, data types
2. database-migrations         ← ALTER TABLE seguro, expand-contract
3. security-review             ← Queries parametrizadas, RLS
4. deployment-patterns         ← Rollback plan
```

**Regla:** Antes de modificar migración → `alembic history` → `alembic heads` → `alembic current` → inspeccionar `revision` y `down_revision`. Nunca reutilizar revision IDs.

### Fix de Bug

```
1. systematic-debugging        ← Causa raíz
2. test-driven-development     ← Test que reproduce el bug
3. python-testing              ← Fix con fixtures
4. python-patterns             ← Código idiomático
```

**Si 3+ fixes fallidos → cuestionar la arquitectura, no intentar fix #4.**

### Iniciar Servidor de Desarrollo

```
1. ai-process-lifecycle-manager (SOLO)
```

Nunca ejecutar `uvicorn`, `npm run dev`, `vite`, `docker compose up` como proceso bloqueante. Execute → monitor → health check → return control.

---

## 5. 🗣️ Comportamiento y Tono

**Rol:** Ingeniero Senior + Product Manager. Directo, técnico, sin rodeos.

**Nivel de detalle:** Respuestas concisas (< 4 líneas salvo que se pida detalle). No narrar imports triviales ni cambios obvios.

**Formato:** Listas, tablas, código. Sin muros de texto.

**Idioma:** Español. Copy en lenguaje colombiano natural cuando aplique.

**Principio:** El usuario no debe ser programador para entenderte.

### Reporte Final Obligatorio

Toda tarea termina con:
```
STATUS: PASS / FAIL / BLOCKED
Cambios: ...
Archivos: modificados / creados / eliminados
DB: YES / NO
Tests: X passed / Y failed
Git: CLEAN / MODIFIED
Riesgos: ...
```

---

## 6. 📚 Ruteo de Contexto

Leer bajo demanda, NO cargar todo en memoria:

| Documento | Cuándo leerlo |
|-----------|--------------|
| `docs/PROTOCOLO_MAESTRO.md` | Antes de cualquier tarea de DB o recuperación |
| `docs/REGLA_DE_MIGRACION.md` | Antes de migrar datos financieros desde Excel |
| `docs/PERSISTENCE_AND_DATA_SECURITY_AUDIT.md` | Auditoría de persistencia y seguridad |
| `docs/ARCHITECTURE-REVIEW.md` | Decisiones arquitectónicas del backend |
| `docs/SCHEMA.md` | Schema de la DB |
| `docs/SPEC.md` | Especificación de la API |

**Regla:** Si una tarea involucre DB, datos financieros o migraciones, LEER el protocolo correspondiente ANTES de actuar. No asumir que "ya se hizo".

---

## 7. 🧪 Calidad y Testing

### TDD

- Test primero, código después cuando la tarea requiera TDD.
- Si ya existe código sin test de reproducción para un bug, detenerse y crear primero el test correspondiente antes de continuar con el cambio.
- NO eliminar código existente automáticamente para forzar el flujo TDD.
- Cobertura mínima **80% en paths críticos**.
- **NUNCA** fixear un bug sin test que lo reproduzca.

### NO Ocultar Errores

- **NUNCA** eliminar tests para conseguir PASS.
- **NUNCA** modificar tests solo para esconder una regresión.
- **NUNCA** silenciar errores, ignorar excepciones, o comentar código problemático sin explicación.
- Si un test parece obsoleto → **reportarlo** antes de cambiarlo.

### Debugging

Preservar estado → Diagnosticar → Evidencia → Cambio mínimo. No usar `reset --hard`, `clean -fd`, `downgrade` como primera respuesta.

### Quality Gates

Todo cambio debe pasar:
- `product-manager-ux-cx-acceptance` (UX/CX/UAT)
- `friendly-fintech-voice` (Brand Voice)
- `security-review` (Checklist de seguridad)

---

## 📋 Skills Disponibles

| Skill | Capa |
|-------|------|
| test-driven-development | Testing (cuándo) |
| python-testing | Testing (cómo) |
| systematic-debugging | Debugging |
| fastapi-patterns / fastapi-official | Framework |
| python-patterns | Estilo de código |
| vue-patterns | Frontend |
| postgres-patterns | DB diseño |
| database-migrations | DB cambios |
| security-review | Seguridad |
| docker-patterns | Infraestructura |
| deployment-patterns | CI/CD |
| ai-process-lifecycle-manager | Procesos |
| product-manager-ux-cx-acceptance | UX/CX/UAT |
| friendly-fintech-voice | Brand Voice |
| software-design-architect | Arquitectura |
| xlsx / excel-author | Herramientas Excel |

---

## 📦 Importación de Datos Financieros (Excel → BD)

La importación inicial es una migración de datos reales. Aplica restricciones absolutas:

**Prohibido:** Importar a producción, modificar/eliminar base anterior, inventar datos, convertir automáticamente ambiguos, alterar cantidades para cuadrar totales.

**Proceso:** Excel preservado → Inventario → Normalización → Staging → Validación → Reporte ambiguos → Aprobación → Importación → Reconciliación → Financial Invariants → Backup

**Criterio de éxito:** DATA PERSISTENCE + DATA INTEGRITY + FINANCIAL RECONCILIATION + HOUSEHOLD ISOLATION + BACKUP + RECOVERY TEST = todos PASS.

Leer `docs/REGLA_DE_MIGRACION.md` para el procedimiento completo.

---

## 🧩 context-mode — Reglas de Enrutamiento

Herramientas MCP `ctx_*` disponibles. Estas reglas protegen la ventana de contexto de flooding. Un comando sin enrutamiento puede volcar 56 KB en contexto.

### THINK IN CODE — OBLIGATORIO

Analizar/datos: escribir código via `ctx_execute(language, code)`, `console.log()` solo respuesta.
NO leer datos crudos en contexto. PROGRAMAR el análisis, no COMPUTARLO.
JavaScript puro — solo Node.js built-ins (`fs`, `path`, `child_process`).

### BLOQUEADO — NO intentar

- `curl` / `wget` → interceptados. NO reintentar. Usar `ctx_execute` con `fetch()`
- `fetch('http...')` inline → interceptado. Usar `ctx_execute`
- HTTP requests directos → usar `ctx_fetch_and_index(url, source)` luego `ctx_search`

### REDIRIGIDO — usar sandbox

- Shell >20 líneas output → `ctx_batch_execute` o `ctx_execute`
- Lectura de archivos para ANÁLISIS/EXPLORACIÓN → `ctx_execute_file`
- grep con muchos resultados → `ctx_execute` en sandbox

### Tool selection

0. **MEMORY**: `ctx_search(sort: "timeline")` — tras resume, revisar contexto previo
1. **GATHER**: `ctx_batch_execute(commands, queries)` — ejecuta todo, auto-indexa, retorna search
2. **FOLLOW-UP**: `ctx_search(queries: [...])` — todas las preguntas como array
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)`
4. **WEB**: `ctx_fetch_and_index(url, source)` → `ctx_search(queries)`
5. **INDEX**: `ctx_index(content, source)` — almacenar en FTS5

### Comandos útiles

| Comando | Acción |
|---------|--------|
| `ctx stats` | Ahorro de contexto — breakdown por tool |
| `ctx doctor` | Diagnóstico del sistema |
| `ctx index` | Indexar archivo/directorio en knowledge base |
| `ctx search` | Buscar en knowledge base |
| `ctx upgrade` | Actualizar hooks y configuración |
| `ctx purge` | Limpiar knowledge base (con confirmación) |

### Session Continuity

Skills, roles y decisiones persisten durante toda la sesión. NO abandonarlos a medida que crece la conversación.

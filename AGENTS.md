# AGENTS.md — Reglas del Proyecto

## Proyecto

Sistema operativo financiero familiar para hogares colombianos.
Administrar economía real de manera simple, privada y rápida.

## Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Frontend**: Vue.js 3 (Composition API), Pinia, Vue Router, Vite, Chart.js
- **DB**: PostgreSQL 16 (producción) + SQLite (desarrollo)
- **Auth**: JWT (python-jose), bcrypt, passlib
- **Testing**: pytest, pytest-asyncio, httpx
- **Deploy**: Docker, docker-compose
- **Moneda**: COP (pesos colombianos)

## Skills Instaladas (15)

| Skill | Capa |
|-------|------|
| test-driven-development | Testing (cuándo) |
| python-testing | Testing (cómo) |
| systematic-debugging | Debugging |
| fastapi-patterns | Framework |
| fastapi-official | Framework |
| python-patterns | Estilo de código |
| vue-patterns | Frontend |
| postgres-patterns | DB diseño |
| database-migrations | DB cambios |
| security-review | Seguridad |
| docker-patterns | Infraestructura |
| deployment-patterns | CI/CD |
| ai-process-lifecycle-manager | Procesos |
| product-manager-ux-cx-acceptance | UX/CX/UAT |
| friendly-fintech-voice | Brand Voice / UX Writing |
| software-design-architect | Arquitectura de Software |
| xlsx | Herramientas Excel |
| excel-author | Excel financiero |

---

## WORKFLOW DE ACTIVACIÓN POR TAREA

**REGLA OBLIGATORIA**: Antes de ejecutar cualquier tarea, activar las skills en el orden indicado. No saltar pasos. No reordenar.

### Nuevo endpoint FastAPI

```
1. test-driven-development    ← Escribir test fallido primero
2. python-testing              ← Cómo escribir el test (fixtures, parametrize)
3. fastapi-patterns            ← Estructura: DI, auth, service layer, response_model
4. python-patterns             ← Código Python idiomático dentro de services
5. security-review             ← Checklist post-implementación
```

### Migración de Base de Datos

```
1. postgres-patterns           ← Diseño: tipos correctos, índices, data types
2. database-migrations         ← Cambio: ALTER TABLE seguro, expand-contract, batch
3. security-review             ← Verificar: queries parametrizadas, RLS
4. deployment-patterns         ← CI/CD: pipeline, rollback plan
```

### Fix de Bug

```
1. systematic-debugging        ← Investigar causa raíz (NO fixear sin diagnosticar)
2. test-driven-development     ← Escribir test fallido que reproduce el bug
3. python-testing              ← Implementar test con fixtures y parametrize
4. python-patterns             ← Código idiomático en el fix
```

**REGLA CRÍTICA**: Si 3+ fixes fallidos → questionar la arquitectura, no intentar fix #4.

### Docker Setup

```
1. docker-patterns             ← Dockerfile multi-stage, Compose, healthcheck
2. ai-process-lifecycle-manager ← No bloquear el agente en compose up
3. deployment-patterns         ← CI/CD: build image, push, rolling deploy
4. security-review             ← Container: non-root, no secrets in layers
```

### Iniciar Servidor de Desarrollo

```
1. ai-process-lifecycle-manager (SOLO)
```

**REGLA**: Nunca ejecutar `uvicorn`, `npm run dev`, `vite`, `docker compose up` como proceso bloqueante. Siempre: execute → monitor → detect ready → health check → return control.

### Excel Financiero

```
1. excel-author                ← Convenciones: azul=inputs, fórmulas, tab Checks
2. xlsx                        ← Tooling: scripts CLI para crear/editar/recalc
```

**REGLA**: Cada cálculo debe ser fórmula Excel, nunca valor computado en Python.

### Deploy a Producción

```
1. deployment-patterns         ← Estrategia: rolling/blue-green/canary
2. security-review             ← Pre-deploy checklist completo
3. database-migrations         ← Migraciones backward-compatible
4. docker-patterns             ← Imagen reproducible, healthcheck
```

### Validación UX/CX/UAT

```
1. product-manager-ux-cx-acceptance ← Product Thinking → User Journey → UAT → Heuristics
2. vue-patterns                      ← Validar Composition API, componentes, accesibilidad
3. security-review                   ← Verificar inputs, XSS, CSRF en formularios
```

**REGLA**: Una funcionalidad técnicamente correcta NO está terminada si el usuario no puede comprenderla, utilizarla o completar su objetivo.

### Escritura de Copy / UX Writing

```
1. friendly-fintech-voice          ← Brand Voice: cercanía, claridad, lenguaje colombiano natural
2. product-manager-ux-cx-acceptance ← Validar: empty states, loading states, mensajes de error/éxito
3. vue-patterns                    ← Implementar: componentes, formularios, feedback visual
```

**REGLA**: Cada mensaje, botón, notificación y error debe pasar: 3-Second Test, WhatsApp Test, Bank Test.

### Diseño / Arquitectura de Software

```
1. software-design-architect      ← SOLID, KISS, DRY, YAGNI, patrones, DDD, CQRS
2. python-patterns                 ← Idiomático: type hints, EAFP, dataclasses
3. fastapi-patterns                ← DI, service layer, response_model
4. test-driven-development         ← Tests que validan contratos y comportamiento
5. systematic-debugging             ← Si hay bugs de diseño: causa raíz primero
```

**REGLA**: La mejor arquitectura es la que resuelve el problema actual con la menor complejidad necesaria. No sobreingenierizar.

---

## Reglas Generales

### Seguridad
- Nunca hardcodear secrets, API keys, tokens, passwords
- Siempre usar variables de entorno
- `.env` nunca en git
- Queries SQL siempre parametrizadas
- Rate limiting en todos los endpoints públicos

### Testing
- TDD estricto: test primero, código después
- Si escribiste código antes del test → borrar y empezar de nuevo
- Cobertura mínimo 80% en paths críticos
- Nunca fixear bugs sin test que los reproduzca

### Base de Datos
- Nunca alterar producción manualmente
- Migraciones forward-only en producción
- Separar DDL de DML
- `CREATE INDEX CONCURRENTLY` para índices en tablas existentes
- Columnas nuevas siempre nullable o con default

### Git
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Nunca force push sin `--force-with-lease`
- Verificar `git status` y `git diff` antes de cualquier operación

### Arquitectura
- Clean Architecture: domain → application → infrastructure → presentation
- Money value object usa `Decimal` (nunca `float`)
- Multi-tenant via `household_id`
- Role-based access: Owner/Member/Viewer

### Procesos
- Clasificar cada comando: SHORT / LONG / PERSISTENT
- Procesos persistentes → ejecución asíncrona → health check → return control
- Nunca esperar indefinidamente
- Idempotency: si el servicio ya existe, no crear otro

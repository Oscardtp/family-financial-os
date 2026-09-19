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

## Skills Instaladas (16)

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

## Decisiones y Hechos del Proyecto (Referencia Rápida)

**Documentos de referencia:**
- `docs/PERSISTENCE_AND_DATA_SECURITY_AUDIT.md` — Auditoría completa de persistencia y seguridad (2026-09-18)
- `docs/REGLA_DE_MIGRACION.md` — Regla de migración de datos financieros desde Excel
- `docs/ARCHITECTURE-REVIEW.md` — Revisión de arquitectura del backend

Estos puntos son conocimiento del proyecto; tenlos en cuenta antes de implementar:

- **Calendario único**: El proyecto tiene una pantalla/Calendario dedicada. Los calendarios embebidos en otras vistas se eliminan para evitar duplicidad.
- **Diseño 100% responsive**: Toda UI debe funcionar en mobile y desktop.
- **Idioma**: Responder y redactar copy siempre en español (lenguaje colombiano natural cuando aplique).
- **Money = Decimal**: Nunca usar `float` para dinero. El VO `Money` usa `Decimal` con cuantización a 2 decimales.
- **InterestRate engine**: Existe `RateEngine.to_monthly_rate(InterestRate)` en `backend/app/financial_engine/rate_engine.py`. Todos los cálculos de tasa deben usarlo, nunca `/1200` ni fórmulas inline.
- **RateType enum**: `EA`, `EM`, `NOMINAL`, `DAILY`. Default = `EA`.
- **Frontend rate_type selector**: NewDebtModal y EditDebtModal ya incluyen selector. Si agregas forms de deuda, usa el mismo enum y env00eda `interest_rate_type` en el payload.
- **useFormattedNumber**: Los composables `onInput` y `onFocus` requieren el evento nativo. Si llamas a estos handlers sin evento, `event.target` lanza `TypeError`.
- **NaN pitfall en Debts.vue**: Al sumar `current_balance + minimum_payment` desde la API, usar `Number(...)` para coerción. Si la API devuelve string/null, la suma produce `NaN`.
- **Quality gates**: Todo cambio debe pasar por `product-manager-ux-cx-acceptance` y `friendly-fintech-voice` antes de considerarse finalizado.
- **Tests**: TDD estricto. Cobertura mínima 80% en paths críticos. Nunca fixear bugs sin test que los reproduzca.
- **Alembic/SQLite**: Las migraciones usan `PRAGMA table_info` para idempotencia. Tests usan `Base.metadata.create_all`, no alembic.
- **Multi-tenant**: Todo acceso por `household_id`. Roles: Owner/Member/Viewer.
- **Clean Architecture**: domain → application → infrastructure → presentation.

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
- SQLite: usar `server_default` para NOT NULL en migraciones add-column

### Git
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Nunca force push sin `--force-with-lease`
- Verificar `git status` y `git diff` antes de cualquier operación

### Arquitectura
- Clean Architecture: domain → application → infrastructure → presentation
- Money value object usa `Decimal` (nunca `float`)
- InterestRate value object + RateEngine para todas las conversiones de tasa
- Multi-tenant via `household_id`
- Role-based access: Owner/Member/Viewer

### Procesos
- Clasificar cada comando: SHORT / LONG / PERSISTENT
- Procesos persistentes → ejecución asíncrona → health check → return control
- Nunca esperar indefinidamente
- Idempotency: si el servicio ya existe, no crear otro

### Frontend
- Composable `useFormattedNumber`: `onInput` y `onFocus` requieren el evento nativo
- En listas de deudas (`Debts.vue`), coerción numérica con `Number(...)` antes de sumar para evitar `NaN`
- Mantener selector `rate_type` sincronizado con backend enum (`EA`, `EM`, `nominal`, `daily`)
- Labels de tasa: mostrar "Tasa Interés" (no "Tasa Mensual") cuando se refiere a la tasa anual

### Importación de Datos Financieros (Excel → BD)

**REGLA**: La importación inicial desde Excel es una migración de datos financieros reales. Aplica las siguientes restricciones absolutas.

**Prohibido:**
- Importar directamente a producción
- Modificar la base anterior
- Eliminar la base anterior
- Sobrescribir registros existentes sin identificación explícita
- Inventar categorías, cuentas, fechas o saldos
- Convertir automáticamente datos ambiguos
- Crear transacciones a partir de datos que no representen movimientos reales
- Convertir automáticamente pagos recurrentes en transacciones
- Convertir proyecciones en transacciones reales
- Alterar cantidades para hacer coincidir un total esperado

**Proceso obligatorio (12 pasos):**
```
Excel original
    ↓
Archivo preservado sin modificar
    ↓
Lectura / inventario
    ↓
Normalización
    ↓
Staging
    ↓
Validación
    ↓
Reporte de registros ambiguos
    ↓
Aprobación
    ↓
Importación
    ↓
Reconciliación
    ↓
Financial Invariants
    ↓
Backup
```

**Registros ambiguos:** Si un registro no puede clasificarse con seguridad, NO se importa automáticamente. Debe aparecer en un reporte con: fila, descripción, valor, fecha, problema y estado `REQUIERE REVISIÓN`.

**Reconciliación obligatoria:**
```
Total Excel = Total importado + Total rechazado + Total pendiente de revisión
```
Debe ser matemáticamente explicable.

**Snapshot:** Antes de considerar terminada la migración, generar conteos y totales (cuentas, transacciones, ingresos, gastos, transferencias, deudas, pagos de deuda, ahorros, inversiones, metas, saldos) y comparar con el Excel original.

**Criterio de éxito:** La migración solamente es exitosa cuando:
```
DATA PERSISTENCE = PASS
DATA INTEGRITY = PASS
FINANCIAL RECONCILIATION = PASS
HOUSEHOLD ISOLATION = PASS
BACKUP = PASS
RECOVERY TEST = PASS
```

---

## Protocolos Operativos (Obligatorios)

**DOCUMENTOS DE REFERENCIA PERMANENTE:**
- `docs/REGLA_DE_MIGRACION.md` — Regla de migración de datos financieros desde Excel
- `docs/PROTOCOLO_MAESTRO.md` — Protocolo maestro de recuperación, desarrollo y QA

**REGLA:** El agente DEBE leer y seguir estos protocolos antes de cualquier tarea que involucre base de datos, datos financieros, o migraciones. No asumir que "ya se hizo" sin verificar.

### Estado Operativo Actual

El proyecto esta en modo:

```
DATABASE RECOVERY MODE
```

No desarrollar nuevas funcionalidades financieras hasta completar todas las fases del Protocolo Maestro (Fase 0 a Fase 6).

### Ciclo de Desarrollo Obligatorio

Después de recuperar la DB, toda funcionalidad debe seguir:

```
ANALIZAR → DISEÑAR → IMPLEMENTAR → MIGRAR → TESTEAR → PERSISTIR → REINICIAR → VERIFICAR → SEGURIDAD → INTEGRIDAD FINANCIERA → REGRESIÓN → QA GATE → READY
```

### Regla de Pausa Operativa

Entre cada fase del protocolo, el agente DEBE:
1. Resumir lo realizado
2. Documentar decisiones clave tomadas
3. Confirmar si todo va de acuerdo al plan
4. Esperar confirmación antes de continuar a la siguiente fase

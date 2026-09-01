# Plan de Refactorización — Family Financial OS

> **Fecha:** 2026-08-26  
> **Estado:** Pendiente de ejecución  
> **Objetivo:** Mejorar mantenibilidad a largo plazo y garantizar responsive completo

---

## Contexto del Proyecto

### Qué es
Sistema operativo financiero familiar para hogares colombianos. Administra economía real de manera simple, privada y rápida.

### Stack
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Frontend:** Vue.js 3 (Composition API), Pinia, Vue Router, Vite, Chart.js
- **DB:** PostgreSQL 16 (producción) + SQLite (desarrollo)
- **Auth:** JWT (python-jose), bcrypt, passlib
- **Testing:** pytest, pytest-asyncio, httpx
- **Deploy:** Docker, docker-compose
- **Moneda:** COP (pesos colombianos)

### Estado actual (post-sprint Tyba)
Se implementaron mejoras UX/CX en la sección de Metas y el botón FAB (+):
- Diseño visual inspirado en Tyba (colores, gradientes, sombras, tipografía)
- Auto-cálculo inteligente en formulario de metas
- Filtros y ordenamiento de metas
- Feedback visual al crear meta (scroll + animación)
- Corrección de tildes en todos los formularios
- Fondos tintados por sección en Dashboard

---

## Análisis de Calidad Actual

### Frontend

| Área | Rating | Problema principal |
|------|--------|-------------------|
| Architecture | 🟡 | Goals.vue es un monolito (1,481 líneas) |
| Code Quality | 🔴 | `formatMoney` en 6+ archivos, `.card` en 19 archivos, `.btn` en 22 archivos |
| Component Size | 🔴 | Goals.vue = 7.4x el umbral de 200 líneas |
| Responsiveness | 🔴 | Goals.vue tiene CERO media queries |
| State Management | 🔴 | `window.dispatchEvent` como event bus; Pinia subutilizado |
| CSS Architecture | 🔴 | Duplicación masiva en bloques scoped; tokens existen pero no se usan |
| Type Safety | 🟡 | Sin TypeScript; validación de props inconsistente |
| Performance | 🟡 | Mutación de objetos reactivos; setTimeout hacks |

### Backend

| Área | Rating | Problema principal |
|------|--------|-------------------|
| Project Structure | 🟡 | `pyproject.toml` sin metadata; `.env` en repo |
| API Architecture | 🟡 | Sin capa de servicio; lógica en route handlers |
| Database Layer | 🟡 | Sin índices en `household_id`; UUID como String(36) |
| Service Layer | 🔴 | Directorio `application/services/` vacío |
| Schema Validation | 🟢 | Pydantic v2 bien usado |
| Error Handling | 🟢 | Excepciones de dominio, handlers personalizados |
| Security | 🟡 | SECRET_KEY con fallback; sin rate limiting; sin token blacklist |
| Testing | 🟡 | Solo 5 tests API + ~25 integración; 2 tests con probables fallos |

---

## Hallazgos Críticos Detallados

### Frontend — Duplicación de CSS

| Clase | Archivos que la redefinen | Ya existe en views.css |
|-------|--------------------------|------------------------|
| `.card` | 19 archivos | Línea 11 |
| `.btn` | 22 archivos | Línea 110 |
| `.modal-overlay` | 10 archivos | Línea 298 |
| `.empty-state` | 7-11 archivos | Línea 28 |
| `.loading-state` | 7-11 archivos | Línea 24 |

### Frontend — formatMoney reimplementado

| Archivo | Línea |
|---------|-------|
| `Goals.vue` | 480 |
| `Debts.vue` | 182 |
| `Accounts.vue` | 284 |
| `DebtCalendar.vue` | 85 |
| `DebtSummary.vue` | 30 |
| `AmortizationModal.vue` | 117 |

Mientras `useCurrency.js` ya provee `fmt()` y `fmtFull()`.

### Backend — Lógica en route handlers

| Endpoint | Líneas de lógica de negocio |
|----------|---------------------------|
| `transactions.py` | ~90 líneas (validación saldo, auditoría) |
| `dashboard.py` | ~150 líneas (8 repos, budget engine) |
| `debts.py` | ~90 líneas (amortización, balance) |
| `recurring_payments.py` | ~50 líneas (procesamiento, transacción) |

### Backend — Sin índices en DB

```python
# Cada repository filtra por household_id pero NO tiene índice
class AccountModel(Base):
    household_id = Column(String(36))  # Sin índice
class TransactionModel(Base):
    account_id = Column(String(36))    # Sin índice
```

### Backend — Atomicidad comprometida

```python
# transactions.py:82-127
await account_repo.deduct_balance(...)  # Puede fallar
await transaction_repo.create(...)       # No se ejecuta
# No hay session.commit() explícito
```

---

## Plan de Acción por Fases

### FASE 0: Preparación (Seguridad)
**Duración:** 30 minutos  
**Riesgo:** Ninguno (solo lectura y copias)

**Pasos:**
1. Crear rama `git checkout -b refactor/phase-0-backup`
2. Copiar seguridad de archivos críticos:
   - `frontend/src/views/Goals.vue` → `Goals.vue.bak`
   - `frontend/src/views/Dashboard.vue` → `Dashboard.vue.bak`
   - `frontend/src/views/Savings.vue` → `Savings.vue.bak`
   - `frontend/src/assets/css/views.css` → `views.css.bak`
   - `frontend/src/assets/design-tokens.css` → `design-tokens.css.bak`
   - `backend/app/presentation/v1/transactions.py` → `transactions.py.bak`
   - `backend/app/presentation/v1/dashboard.py` → `dashboard.py.bak`
   - `backend/app/models.py` → `models.py.bak`
3. Ejecutar `npm run build` y `python -m py_compile` — verificar que todo compila
4. Capturar screenshot del estado actual ( referencia visual )
5. Commit: `chore: backup before refactor phase 0`

**Skills a usar:** `git-github-workflow-assistant`

---

### FASE 1: Descomponer Goals.vue (Frontend)
**Duración:** 2-3 horas  
**Riesgo:** Medio (refactorización de componente grande)  
**Bloqueante:** Ninguna fase depende de esta

**Objetivo:** Convertir Goals.vue de 1,481 líneas a ~5 componentes de <200 líneas cada uno.

**Componentes a crear:**

```
src/components/goals/
├── GoalCard.vue              (~80 líneas) — Tarjeta individual de meta
├── GoalCreateModal.vue       (~120 líneas) — Modal de creación
├── GoalEditModal.vue         (~100 líneas) — Modal de edición
├── GoalContributionModal.vue (~80 líneas) — Modal de aporte
├── GoalDeleteConfirm.vue     (~40 líneas) — Confirmación de eliminación
└── GoalFilters.vue           (~60 líneas) — Toolbar de filtros/ordenamiento
```

**Composable a crear:**

```
src/composables/
└── useGoals.js               (~150 líneas) — Lógica de datos, API, estados
```

**Pasos detallados:**

1. **Crear `GoalCard.vue`**
   - Extraer template del goal card (líneas 51-147 de Goals.vue)
   - Mover estilos scoped del goal card
   - Props: `goal`, `expanded`, `highlighted`
   - Emits: `toggle-expand`, `contribute`, `edit`, `delete`
   - **VALIDAR:** Comparar visualmente con Goals.vue original — mismo icono, badge, montos, progress bar, acciones

2. **Crear `GoalCreateModal.vue`**
   - Extraer modal de creación (líneas 213-298)
   - Incluir `useSmartCalculator` integrado
   - Props: `show`
   - Emits: `close`, `created`
   - **VALIDAR:** Mismo formulario, mismos campos, misma validación, mismo auto-cálculo

3. **Crear `GoalEditModal.vue`**
   - Extraer modal de edición (líneas 305-351)
   - Props: `show`, `goal`
   - Emits: `close`, `updated`
   - **VALIDAR:** Mismos campos (nombre, monto, aporte, fecha, prioridad, goal_type)

4. **Crear `GoalContributionModal.vue`**
   - Extraer modal de aporte (líneas 178-212)
   - Props: `show`, `goal`
   - Emits: `close`, `contributed`
   - **VALIDAR:** Mismo campo monto, mismo campo fecha editable, misma validación

5. **Crear `GoalDeleteConfirm.vue`**
   - Extraer confirmación de eliminación (líneas 353-364)
   - Props: `show`, `goal`
   - Emits: `close`, `confirm`
   - **VALIDAR:** Mismo mensaje, mismo comportamiento

6. **Crear `GoalFilters.vue`**
   - Extraer toolbar de filtros (líneas 50-66)
   - Props: `filterType`, `sortBy`
   - Emits: `update:filterType`, `update:sortBy`
   - **VALIDAR:** Mismos botones pill, mismo select, mismos estilos Tyba

7. **Crear `useGoals.js` composable**
   - Extraer: `loadData`, `createGoal`, `editGoal`, `deleteGoal`, `contribute`, `goalProgress`, `monthsRemaining`, `formatMoney`, `formatDate`
   - Mover refs: `goals`, `loading`, `error`, `expandedGoal`, `highlightedGoalId`
   - **VALIDAR:** `formatMoney` usa `useCurrency.js` (no reimplementar)
   - **VALIDAR:** Evento `goal-created` sigue funcionando

8. **Refactorizar `Goals.vue`**
   - Importar todos los componentes y composable
   - Goals.vue debería quedar ~100 líneas (solo orquestación)
   - **VALIDAR:** `npm run build` sin errores
   - **VALIDAR:** Todas las funciones siguen disponibles:
     - Crear meta (modal + API + toast + scroll highlight)
     - Editar meta (modal + API + toast)
     - Eliminar meta (confirmación + API + toast)
     - Contribuir a meta (modal + fecha editable + API + toast)
     - Filtros (Todas/Ahorro/Inversión)
     - Ordenamiento (Nombre/Prioridad/Progreso/Fecha)
     - Empty state con CTA
     - Resumen general (activas, acumulado, objetivo, progress bar)
     - Metas completadas

9. **Comparación final**
   - Abrir Goals.vue original (backup) y Goals.vue refactorizado lado a lado
   - Verificar: mismos colores, fonts, spacing, shadows, border-radius
   - Verificar: mismo comportamiento en mobile ( responsive )
   - Verificar: misma accesibilidad (aria-labels, roles)

**Skills a usar:** `vue-patterns`, `fastapi-patterns`, `test-driven-development`

**Checklist de entrega FASE 1:**
- [ ] `npm run build` sin errores
- [ ] Goals.vue < 200 líneas
- [ ] Cada componente < 200 líneas
- [ ] `useGoals.js` extraído correctamente
- [ ] No hay `formatMoney` duplicado (usar `useCurrency`)
- [ ] Evento `goal-created` sigue funcionando
- [ ] Responsive: form-row se apila en mobile
- [ ] Responsive: toolbar se adapta en mobile
- [ ] Responsive: goal-card se adapta en mobile
- [ ] Todos los modales funcionan igual
- [ ] Filtros y ordenamiento funcionan
- [ ] Empty state con CTA visible
- [ ] Animación de highlight al crear meta
- [ ] Mismos colores Tyba (primary #2f71e5, neutrals)
- [ ] Mismas fonts (Poppins headings, Inter body)

---

### FASE 2: Limpiar Duplicación CSS (Frontend)
**Duración:** 1-2 horas  
**Riesgo:** Bajo (cambios cosméticos)  
**Bloqueante:** FASE 1 completada

**Objetivo:** Eliminar todas las redefiniciones de `.card`, `.btn`, `.modal-overlay`, `.empty-state` en scoped styles.

**Pasos detallados:**

1. **Auditar `views.css`**
   - Verificar que todas las clases globales están definidas correctamente
   - Agregar clases faltantes (`.goal-card`, `.filter-btn`, `.sort-select`)
   - Asegurar que los estilos globales son suficientes para todos los componentes

2. **Limpiar `Goals.vue` (refactorizado)**
   - Eliminar `.card` redefinido (usar global de views.css)
   - Eliminar `.btn` redefinido (usar global)
   - Eliminar `.modal-overlay` redefinido (usar global)
   - Eliminar `.empty-state` redefinido (usar global)
   - Mantener solo estilos específicos del componente

3. **Limpiar `Dashboard.vue`**
   - Eliminar `.card` redefinido (línea 296)
   - Eliminar `.btn` redefinido (línea 352)
   - Mantener `.dash-*` y `.side-*` específicos

4. **Limpiar `Savings.vue`**
   - Eliminar `.card` redefinido (línea 170)
   - Mantener `.savings-*` específicos

5. **Limpiar otros archivos** (en orden de impacto)
   - `Budgets.vue` — `.card`, `.btn`, `.modal-overlay`
   - `Categories.vue` — `.card`
   - `Config.vue` — `.card`
   - `Household.vue` — `.card`
   - `Audit.vue` — `.card`
   - `Patrimony.vue` — `.card`, `.modal-overlay`
   - `Transactions.vue` — `.card`
   - `Accounts.vue` — `.card`, `.btn`, `.modal-overlay`
   - `Debts.vue` — `.card`, `.btn`, `.modal-overlay`

6. **Unificar `formatMoney`**
   - En cada archivo que reimplementa `formatMoney`, reemplazar por `import { useCurrency } from '@/composables/useCurrency'`
   - `const { fmt } = useCurrency()`
   - Reemplazar `formatMoney(valor)` por `fmt(valor)`
   - **VALIDAR:** Cada archivo compila correctamente

7. **Comparación visual**
   - Tomar screenshot de cada vista antes/después
   - Verificar: mismos colores, spacing, border-radius
   - Verificar: responsive no se rompió

**Skills a usar:** `vue-patterns`, `security-review`

**Checklist de entrega FASE 2:**
- [ ] `npm run build` sin errores
- [ ] Cero redefiniciones de `.card` en scoped styles
- [ ] Cero redefiniciones de `.btn` en scoped styles
- [ ] Cero redefiniciones de `.modal-overlay` en scoped styles
- [ ] `formatMoney` solo existe en `useCurrency.js`
- [ ] Cada vista mantiene su apariencia visual
- [ ] Responsive no se rompió

---

### FASE 3: Service Layer Backend
**Duración:** 2-3 horas  
**Riesgo:** Alto (cambios en lógica de negocio)  
**Bloqueante:** Ninguna fase depende de esta

**Objetivo:** Extraer lógica de negocio de route handlers a servicios.

**Servicios a crear:**

```
backend/app/application/services/
├── transaction_service.py    (~150 líneas)
├── dashboard_service.py      (~200 líneas)
├── debt_service.py           (~150 líneas)
└── recurring_payment_service.py (~100 líneas)
```

**Pasos detallados:**

1. **Crear `transaction_service.py`**
   - Extraer de `transactions.py:42-133`:
     - Validación de saldo
     - Deducción de saldo
     - Creación de transacción
     - Auditoría
   - Envolver en transacción explícita (`session.commit()`)
   - **VALIDAR:** Mismos tests pasan

2. **Crear `dashboard_service.py`**
   - Extraer de `dashboard.py:24-177`:
     - Aggregación de 8 repositorios
     - Budget engine
     - Alert generation
   - **VALIDAR:** Dashboard muestra mismos datos

3. **Crear `debt_service.py`**
   - Extraer de `debts.py:66-157`:
     - Cálculo de amortización
     - Actualización de balance
     - Registro de pagos
   - **VALIDAR:** Deudas funcionan igual

4. **Crear `recurring_payment_service.py`**
   - Extraer de `recurring_payments.py:87-137`:
     - Procesamiento de pagos
     - Creación de transacción asociada
   - Reusar lógica de `mark_as_paid` (DRY)
   - **VALIDAR:** Pagos recurrentes funcionan

5. **Actualizar route handlers**
   - Los handlers solo deben: validar input, llamar servicio, retornar respuesta
   - Máximo 15-20 líneas por handler
   - **VALIDAR:** Todos los endpoints responden igual

6. **Tests de servicio**
   - Crear tests unitarios para cada servicio (sin HTTP)
   - Mockear repositorios
   - **VALIDAR:** `pytest` pasa

**Skills a usar:** `fastapi-patterns`, `python-patterns`, `test-driven-development`, `security-review`

**Checklist de entrega FASE 3:**
- [ ] `python -m py_compile` sin errores en todos los servicios
- [ ] Route handlers < 20 líneas cada uno
- [ ] Services contienen toda la lógica de negocio
- [ ] Transacciones son atómicas (commit explícito)
- [ ] Tests de servicio pasan
- [ ] Todos los endpoints responden igual
- [ ] No hay lógica de negocio en route handlers

---

### FASE 4: Índices DB y Seguridad Backend
**Duración:** 1-2 horas  
**Riesgo:** Medio (migraciones de DB)  
**Bloqueante:** FASE 3 completada

**Objetivo:** Agregar índices de performance y cerrar brechas de seguridad.

**Pasos detallados:**

1. **Crear migración de índices**
   ```python
   # Índices a agregar:
   - account.household_id
   - transaction.account_id
   - transaction.household_id
   - debt.household_id
   - savings_goal.household_id
   - recurring_payment.household_id
   - budget.household_id
   - notification.user_id
   ```

2. **Usar `CREATE INDEX CONCURRENTLY`** (producción sin downtime)

3. **Seguridad**
   - Bloquear `SECRET_KEY` default en producción (no solo advertir)
   - Agregar rate limiting a `/auth/login` y `/auth/register`
   - Implementar refresh token blacklist (o rotación con jti)
   - Excluir `password_hash` del dict retornado por `get_current_user`

4. **Tests de seguridad**
   - Test: token expirado es rechazado
   - Test: refresh token revocado no funciona
   - Test: brute-force login es bloqueado
   - Test: role escalation es rechazado

**Skills a usar:** `postgres-patterns`, `database-migrations`, `security-review`, `deployment-patterns`

**Checklist de entrega FASE 4:**
- [ ] Migración creada con `CREATE INDEX CONCURRENTLY`
- [ ] Todos los `household_id` tienen índice
- [ ] `SECRET_KEY` bloquea en producción con default
- [ ] Rate limiting activo en auth endpoints
- [ ] Refresh token blacklist funciona
- [ ] `password_hash` nunca se expone
- [ ] Tests de seguridad pasan

---

### FASE 5: Pinia Store y Event Bus (Frontend)
**Duración:** 1-2 horas  
**Riesgo:** Medio (cambio de patrón de estado)  
**Bloqueante:** FASE 1 completada

**Objetivo:** Reemplazar `window.dispatchEvent` con Pinia store compartido.

**Pasos detallados:**

1. **Crear `stores/goals.js`**
   ```javascript
   export const useGoalsStore = defineStore('goals', () => {
     const goals = ref([])
     const loading = ref(false)
     
     async function fetchGoals() { ... }
     async function createGoal(data) { ... }
     async function updateGoal(id, data) { ... }
     async function deleteGoal(id) { ... }
     async function contribute(id, data) { ... }
     
     return { goals, loading, fetchGoals, createGoal, ... }
   })
   ```

2. **Migrar `Goals.vue`** para usar el store
3. **Migrar `Dashboard.vue`** para usar el store (elimina fetch duplicado)
4. **Eliminar `window.dispatchEvent('goal-created')`**
5. **Migrar `QuickAddFab.vue`** para usar el store
6. **Eliminar composable `useGoals.js`** si el store lo reemplaza completamente

**Skills a usar:** `vue-patterns`, `test-driven-development`

**Checklist de entrega FASE 5:**
- [ ] `stores/goals.js` creado
- [ ] Cero `window.dispatchEvent` para `goal-created`
- [ ] Cero `window.addEventListener` para `goal-created`
- [ ] Dashboard y Goals comparten datos del store
- [ ] Solo 1 fetch a `/savings/goals` (no 3)
- [ ] `npm run build` sin errores
- [ ] Funcionamiento identico

---

### FASE 6: Tests y Validación Final
**Duración:** 2-3 horas  
**Riesgo:** Ninguno (solo lectura y escritura de tests)  
**Bloqueante:** FASES 1-5 completadas

**Objetivo:** Cobertura de tests completa y validación de responsive.

**Pasos detallados:**

1. **Tests Frontend**
   - Test: `GoalCard` renderiza correctamente
   - Test: `GoalCreateModal` abre/cierra
   - Test: `GoalEditModal` carga datos de meta
   - Test: `GoalContributionModal` valida monto
   - Test: Filtros funcionan (Todas/Ahorro/Inversión)
   - Test: Ordenamiento funciona (Nombre/Prioridad/Progreso/Fecha)
   - Test: Store de goals funciona correctamente

2. **Tests Backend**
   - Test: `TransactionService` crea transacción atómicamente
   - Test: `DashboardService` agrega datos correctamente
   - Test: `DebtService` calcula amortización
   - Test: Auth: token expirado rechazado
   - Test: Auth: refresh token revocado rechazado
   - Test: Rate limiting funciona

3. **Validación Responsive**
   - Probar en: 320px, 375px, 414px, 768px, 1024px, 1440px
   - Verificar: Goals toolbar se apila en mobile
   - Verificar: Goal cards se adaptan
   - Verificar: Modales no se desbordan
   - Verificar: Dashboard sidebar se colapsa
   - Verificar: Touch targets >= 44px

4. **Validación Visual**
   - Comparar screenshots antes/después de cada fase
   - Verificar: colores Tyba consistentes
   - Verificar: fonts Poppins/Inter correctas
   - Verificar: gradientes y sombras correctas
   - Verificar: border-radius pill en botones

**Skills a usar:** `python-testing`, `test-driven-development`, `security-review`

**Checklist de entrega FASE 6:**
- [ ] Todos los tests pasan (`pytest` + `npm run lint`)
- [ ] Responsive funciona en 320px-1440px
- [ ] Touch targets >= 44px
- [ ] Modales no se desbordan
- [ ] Colores Tyba consistentes
- [ ] Fonts correctas
- [ ] Sin regressions visuales

---

## Resumen para No Programadores

### Qué se hizo en el sprint Tyba
Se mejoró la apariencia visual de la sección de Metas para que sea más moderna y fácil de usar:
- **Colores más atractivos:** Azul cálido como Tyba, textos más legibles
- **Botones redondeados:** Estilo "pill" como las apps modernas
- **Auto-cálculo:** Al poner fecha objetivo, calcula cuánto ahorrar al mes automáticamente
- **Filtros:** Se puede filtrar por tipo de meta (Ahorro/Inversión) y ordenar por nombre, prioridad, progreso o fecha
- **Feedback visual:** Al crear una meta, la pantalla hace scroll automático hacia ella con una animación de resaltado
- **Corrección de errores:** Se corrigieron tildes en todos los formularios

### Qué se va a hacer en la refactorización

**Fase 0 — Preparación (seguridad)**
> Hacemos copias de seguridad de todos los archivos importantes antes de tocar nada. Si algo sale mal, podemos volver al estado anterior.

**Fase 1 — Separar la página de Metas en partes pequeñas**
> Actualmente, toda la lógica de Metas está en un solo archivo gigante (1,500 líneas). Lo separaremos en archivos pequeños y fáciles de entender: uno para crear metas, otro para editar, otro para aportar, etc. Es como desarmar un mueble grande en cajones organizados.

**Fase 2 — Limpiar estilos duplicados**
> Muchos estilos están escritos 10-20 veces en diferentes archivos. Los centralizaremos en un solo lugar. Si cambiamos el color de un botón, cambia en todas partes automáticamente.

**Fase 3 — Organizar la lógica del servidor**
> La lógica de negocio (cómo se procesan transacciones, cómo se calculan deudas) está mezclada con las peticiones HTTP. La separaremos en "servicios" dedicados, como organizar una cocina: cada utensilio tiene su lugar.

**Fase 4 — Velocidad y seguridad**
> Agregaremos "índices" a la base de datos para que las consultas sean más rápidas. También cerraremos huecos de seguridad: contraseñas más protegidas, límite de intentos de login, tokens más seguros.

**Fase 5 — Compartir datos correctamente**
> Actualmente, cuando creas una meta con el botón (+), la página de Metas no se entera hasta que recargas. Haremos que los datos se compartan correctamente entre pantallas, como una memoria compartida.

**Fase 6 — Pruebas y validación**
> Probaremos todo manual y automáticamente para asegurar que nada se rompió. Verificaremos que se vea bien en celulares, tablets y computadores.

---

## Skills a Utilizar por Fase

| Fase | Skills |
|------|--------|
| FASE 0 | `git-github-workflow-assistant` |
| FASE 1 | `vue-patterns`, `fastapi-patterns`, `test-driven-development` |
| FASE 2 | `vue-patterns`, `security-review` |
| FASE 3 | `fastapi-patterns`, `python-patterns`, `test-driven-development`, `security-review` |
| FASE 4 | `postgres-patterns`, `database-migrations`, `security-review`, `deployment-patterns` |
| FASE 5 | `vue-patterns`, `test-driven-development` |
| FASE 6 | `python-testing`, `test-driven-development`, `security-review` |

---

## Orden de Activación de Skills (por tarea)

### Nuevo endpoint FastAPI
```
1. test-driven-development    ← Escribir test fallido primero
2. python-testing              ← Cómo escribir el test
3. fastapi-patterns            ← Estructura: DI, auth, service layer
4. python-patterns             ← Código idiomático
5. security-review             ← Checklist post-implementación
```

### Migración de DB
```
1. postgres-patterns           ← Diseño: tipos, índices
2. database-migrations         ← Cambio seguro
3. security-review             ← Queries parametrizadas
4. deployment-patterns         ← Rollback plan
```

### Fix de Bug
```
1. systematic-debugging        ← Investigar causa raíz
2. test-driven-development     ← Test que reproduce el bug
3. python-testing              ← Fix con fixtures
4. python-patterns             ← Código idiomático
```

---

## Checklists de Entrega General

### Antes de cada fase
- [ ] Rama de git creada
- [ ] Backup de archivos críticos
- [ ] `npm run build` / `python -m py_compile` pasa
- [ ] Screenshot del estado actual

### Después de cada fase
- [ ] Build pasa sin errores
- [ ] Tests pasan
- [ ] Comparación visual con backup
- [ ] Responsive verificado (mobile)
- [ ] Sin regressions funcionales

### Para release final
- [ ] Todas las fases completadas
- [ ] Cobertura de tests > 80%
- [ ] Responsive funciona en 320px-1440px
- [ ] Lighthouse score > 90
- [ ] Sin console errors
- [ ] Sin warnings de seguridad
- [ ] Documentación actualizada

---

## Archivos Importantes de Referencia

### Frontend
- `frontend/src/assets/design-tokens.css` — Tokens de diseño Tyba
- `frontend/src/assets/css/main.css` — Estilos globales
- `frontend/src/assets/css/views.css` — Estilos compartidos de vistas
- `frontend/src/views/Goals.vue` — Página de metas (a refactorizar)
- `frontend/src/views/Dashboard.vue` — Dashboard principal
- `frontend/src/views/Savings.vue` — Página de ahorros (referencia)
- `frontend/src/components/quickadd/QuickAddFab.vue` — Botón flotante (+)
- `frontend/src/components/quickadd/GoalForm.vue` — Formulario de meta
- `frontend/src/composables/useSmartCalculator.js` — Auto-cálculo
- `frontend/src/composables/useCurrency.js` — Formateo de moneda

### Backend
- `backend/app/main.py` — Entry point
- `backend/app/models.py` — Modelos de DB
- `backend/app/schemas.py` — Schemas Pydantic
- `backend/app/presentation/v1/` — Route handlers
- `backend/app/repositories/` — Acceso a DB
- `backend/app/application/services/` — Lógica de negocio (vacío)
- `backend/app/domain/` — Entidades de dominio
- `backend/tests/` — Tests

---

## Notas para la Próxima Sesión

1. **Empezar por FASE 0** — No saltarse el backup
2. **FASE 1 es la más crítica** — Goals.vue es el mayor problema de mantenibilidad
3. **Comparar visualmente** después de cada paso de FASE 1
4. **No romper responsive** — Verificar en 375px (iPhone) después de cada cambio
5. **Mantener colores Tyba** — Primary #2f71e5, neutrals #141b1f/#6b7a85
6. **Mantener fonts** — Poppins para headings, Inter para body
7. **Event `goal-created`** debe seguir funcionando hasta FASE 5
8. **Backend services** son independientes del frontend — se pueden hacer en paralelo

---

*Documento generado automáticamente. Actualizar después de completar cada fase.*
